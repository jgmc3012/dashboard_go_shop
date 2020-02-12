from store.store import Store
from meli_sdk.sdk.meli import Meli

from store.products.models import Product, Category, Attribute, Picture
from store.models import Seller, BusinessModel

from meli_sdk.models import BulkCreateManager
from math import ceil
import logging
from django.utils import timezone

class Scraper(Meli):

    path = f'/sites/MCO/search'
    def __init__(self):
        Meli.__init__(self)
        self.store = Store()

    def scan_for_seller(self, seller_id):
        params = {
            'seller_id' : seller_id
        }
        result = self.get(self.path, params)
        if not result:
            return []
        total = result['paging']['total'] if result['paging']['total'] <= 1000 else 1000
        limit = result['paging']['limit']
        seller_draw = result['seller']
        products_draw = result['results']

        seller = Seller.objects.get(id=seller_draw['id'])
        seller.nickname = seller_draw['nickname']
        seller.save()

        list_params = [{
            'seller_id' : seller_id,
            'offset' : offset,
            'limit':50,
            'attributes': 'results'
        }for offset in range(limit,total,limit)]
        products_api = self.map_pool_get(
            paths=[self.path]*len(list_params),
            params=list_params
        )

        for product in products_api:
            products_draw += product['results']

        categories = ScraperCategory()

        BM = BusinessModel.objects.get(pk=self.store.SELLER_ID)
        bulk_mgr = BulkCreateManager()

        ids_products = list()
        for product_ in products_draw:
            if (
                (not product_['shipping']['free_shipping']) or
                (not product_['condition'] == 'new')
            ):
                continue
            
            elif (not int(product_['category_id'][3:]) in categories.ids):
                categories.update(product_['category_id'])

            category_id = int(product_['category_id'][3:])
            category_father_id = categories.array[category_id].father
            if not categories.array[category_father_id].approved:
                continue

            cost_price = ceil(product_['price']/BM.trm)
            sales_cost = ceil( (cost_price+BM.shipping_vzla)*(1+BM.meli_tax/100)*(1+BM.utility/100) )
            key_category = category_father_id
            product = Product.objects.get_or_create(
                seller=seller,
                title=product_['title'],
                cost_price=cost_price,
                sale_price= sales_cost,
                provider_sku=product_['id'],
                provider_link=product_['permalink'],
                image=product_['thumbnail'].replace('http','https'),
                category = categories.array[key_category],
                quantity=product_['initial_quantity']
            )
            if product[1]:
                product = product[0]
                ids_products.append(product_['id'])
                for _attribute in product_['attributes']:
                    if _attribute['value_name'] and (350 < len(_attribute['value_name'])):
                        bulk_mgr.add(Attribute(
                            id_meli=_attribute['id'],
                            value=_attribute['value_name'],
                            value_id=_attribute.get('value_id'),
                            product=product
                        ))
        bulk_mgr.done()
        return self.scan_product(ids_products)

    def scan_for_category(self, category):
        params = {
            'offset':0,
            'sort':'relevance',
            'shipping':'mercadoenvios',
            'power_seller':'yes',
            'has_pictures':'yes',
            'shipping_cost':'free',
            'ITEM_CONDITION':2230284,
            'category':f'MCO{category.id}'
        }

        result_draw = self.get(
            self.path,
            params
        )

        result = self.get(self.path, params)
        if not result:
            return []
        total = result['paging']['total'] if result['paging']['total'] <= 10_000 else 10_000
        limit = result['paging']['limit']
        products_draw = result['results']

        list_params = [{
            'offset':offset,
            'sort':'relevance',
            'shipping':'mercadoenvios',
            'power_seller':'yes',
            'has_pictures':'yes',
            'shipping_cost':'free',
            'ITEM_CONDITION':2230284,
            'category':f'MCO{category.id}',
            'attribute':'results'
        }for offset in range(limit,total,limit)]

        logging.info(f'Scrapeando {total} productos')
        products_api = self.map_pool_get(
            paths=[self.path]*len(list_params),
            params=list_params,
            auths=[True]*len(list_params)
        )

        for product in products_api:
            products_draw += product['results']

        BM = BusinessModel.objects.get(pk=self.store.SELLER_ID)
        bulk_mgr = BulkCreateManager(200)

        ids_products = list()
        sellers = ScraperSeller()
        bad_sellers = Seller.objects.filter(bad_seller=True).values_list('id',flat=True)
        for product_ in products_draw:
            seller_id = int(product_['seller']['id'])
            if seller_id in bad_sellers:
                continue
            elif seller_id not in sellers.ids:
                sellers.update(seller_id)

            cost_price = ceil(product_['price']/BM.trm)
            sales_cost = ceil( (cost_price+BM.shipping_vzla)*(1+BM.meli_tax/100)*(1+BM.utility/100))
            product = Product.objects.filter(provider_sku=product_['id']).first()
            if not product:
                product = Product.objects.create(
                    seller=sellers.array[seller_id],
                    title=product_['title'],
                    cost_price=cost_price,
                    sale_price= sales_cost,
                    provider_sku=product_['id'],
                    provider_link=product_['permalink'],
                    image=product_['thumbnail'].replace('http','https'),
                    category = category,
                    quantity=product_['available_quantity']
                )
                for _attribute in product_['attributes']:
                    if _attribute['value_name'] and (350 < len(_attribute['value_name'])):
                        bulk_mgr.add(Attribute(
                            id_meli=_attribute['id'],
                            value=_attribute['value_name'],
                            value_id=_attribute.get('value_id'),
                            product=product
                        ))

            ids_products.append(product_['id'])

        bulk_mgr.done()
        return self.scan_product(ids_products)

    def scan_product(self, list_ids):
        path = '/items'
        params = [{
            'ids': ids,
            'attributes': 'id,pictures,sale_terms',
        } for ids in self.split_ids(list_ids)]
        results = self.map_pool_get(
            [path]*len(params),
            params
        )

        products_draw = {product['body']['id']:product for product in results if product.get('body')}
        products = Product.objects.filter(provider_sku__in=products_draw.keys())
        product_with_img = Picture.objects.filter(product__in=products).values_list('product',flat=True)
        if product_with_img:
            products = products.exclude(id__in=product_with_img)

        bulk_mgr = BulkCreateManager(250)
        for product in products:
            sku = product.provider_sku
            if not products_draw[sku].get('body'):
                logging.warning(f'Error en la peticion de {product}. Res: {products_draw[sku]}')
                continue
            elif not products_draw[sku]['body'].get('pictures'):
                logging.warning(f'Al producto {product} no se le encontraron imagenes')
                continue
            elif products_draw[sku]['body']['sale_terms']:
                for sale_term in products_draw[sku]['body']['sale_terms']:
                    timeout = (sale_term['id'] == 'MANUFACTURING_TIME')
                    if timeout:
                        logging.warning(f"Producto {product} con terminos de entrega, {sale_term['value_name']}")
                        break
                if timeout:
                    continue

            for image in products_draw[sku]['body']['pictures']:
                if 'resources/frontend/statics/processing' in image['secure_url']:
                    logging.warning('Imagen [Procesando por Meli]')
                    continue
                picture = Picture(
                    src=image['secure_url'],
                    product=product
                )
                bulk_mgr.add(picture)
        bulk_mgr.done()

    def update_products(self, products):
        logging.info(f'Actualizando {len(products)} productos. \n')
        list_ids = products.values_list('provider_sku', flat=True)
        path = '/items'
        params = [{
            'ids': ids,
            'attributes': 'id,price,initial_quantity,status',
        } for ids in self.split_ids(list_ids)]
        results = self.map_pool_get(
            [path]*len(params),
            params
        )

        products_draw = {product['body']['id']:product['body'] for product in results}
        BM = BusinessModel.objects.get(pk=self.store.SELLER_ID)
        bulk_mgr = BulkCreateManager()
        for product in products:
            id = product.provider_sku
            if id in products_draw:
                if not products_draw[id].get('initial_quantity'):
                    logging.warning(f'Producto {id} NO ACTUALIZADO')
                    continue
                if not products_draw[id]['status'] == 'active':
                    products_draw[id]['initial_quantity']=0
                logging.info(f"{product.sku}: quantity: {product.quantity} \
-> {products_draw[id]['initial_quantity']}")
                product.quantity = products_draw[id]['initial_quantity']
                cost_price = ceil(products_draw[id]['price']/BM.trm)
                sale_cost = ceil( (cost_price+BM.shipping_vzla)*(1+BM.meli_tax/100)*(1+BM.utility/100) )
                product.cost_price = cost_price
                product.sale_price = sale_cost
                product.last_update = timezone.localtime()
                bulk_mgr.update(product, {'quantity', 'cost_price', 'sale_price', 'last_update'})
        bulk_mgr.done()

class ScraperCategory(Meli):

    category_path = '/categories'
    bulk_mgr = BulkCreateManager()

    def __init__(self):
        Meli.__init__(self)
        self._ids = list()
        self._categories = dict()

    @property
    def ids(self):
        if not self._categories:
            categories = Category.objects.all()
            for category in categories:
                self._categories[category.id] = category
            self._ids = categories.values_list('id', flat=True)
        return self._ids

    @property
    def array(self):
        if not self._categories:
            categories = Category.objects.all()
            for category in categories:
                self._categories[category.id] = category
            self._ids = categories.values_list('id', flat=True)
        return self._categories

    def _set_array(self, id, father, name, approved=False):
        if 'M' == id[0]:
            id = int(id[3:])
        if 'M' == father[0]:
            father = int(father[3:])
        if not id in self.ids:
            self._categories[id] = Category.objects.create(
                id=id,
                father=father,
                name=name,
                approved=approved
            )
            self._ids.append(id)

    def scraping_path(self, category_root):
        result = self.get(
            path=f'{self.category_path}/{category_root}',
            params={'attributes':'id,name,children_categories,total_items_in_this_category,path_from_root'}
        )
        children_categories = result.get('children_categories')
        if result.get('id'):
            current_category_id = int(result['id'][3:])
            current_category = Category.objects.filter(
                id=current_category_id).first()
            if not current_category:
                current_category = Category.objects.create(
                    id=current_category_id,
                    name=result['name']
                )
            elif not children_categories:
                current_category.leaf=True
                current_category.save()
            logging.info(f'Padre {current_category} - {len(children_categories)} subcategorias - {result["total_items_in_this_category"]} Items')
        else:
            logging.warn(result)
        if children_categories:
            next_level = list()
            self._categories = dict()
            root_id = int(result['path_from_root'][0]['id'][3:])
            root = self.array[root_id]
            
            for category in children_categories:
                id = int(category['id'][3:])
                items = int(category['total_items_in_this_category'])
                name = category['name']
                leaf = (items < 10_000)
                if not id in self.ids:
                    self.bulk_mgr.add(Category(
                        id=id,
                        parent=current_category,
                        root=root,
                        name=name,
                        leaf=leaf
                    ))
                logging.info(f'<{id}:{name}[{items} items]>')
                if not leaf:
                    next_level.append(category['id'])

            self.bulk_mgr.done()

            for category in next_level:
                logging.info('-'*30)
                self.scraping_path(category)
                

    def update(self, id):
        if not int(id[3:]) in self.ids:
            path = f'/categories/{id}'
            result = self.get(path)
            name = result['name']
            father = result['path_from_root'][0]['id']
            if int(father[3:]) != int(id[3:]):
                self.update(father)
            self._set_array(id,father,name)

class ScraperSeller(Meli):
    
    def __init__(self):
        Meli.__init__(self)
        self._ids = list()
        self._sellers = dict()

    @property
    def ids(self):
        if not self._sellers:
            sellers = Seller.objects.all()
            for seller in sellers:
                self._sellers[seller.id] = seller
            self._ids = list(sellers.values_list('id', flat=True))
        return self._ids

    @property
    def array(self):
        if not self._sellers:
            sellers = Seller.objects.all()
            for seller in sellers:
                self._sellers[seller.id] = seller
            self._ids = list(sellers.values_list('id', flat=True))
        return self._sellers

    def set_array(self, seller_id,seller_nickname):
        if not seller_id in self.ids:
            self._sellers[seller_id] = Seller.objects.create(
                id=seller_id,
                nickname=seller_nickname
            )
            self._ids.append(seller_id)

    def update(self, id:int):
        if not id in self.ids:
            path = f'/users/{id}'
            result = self.get(path)
            name = result['nickname']
            self.set_array(id,name)