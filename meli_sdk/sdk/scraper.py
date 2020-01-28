from store.store import Store
from meli_sdk.sdk.meli import Meli

from store.products.models import Product, Category, Attribute
from store.models import Seller, BusinessModel

from meli_sdk.models import BulkCreateManager
from math import ceil

class Scraper(Meli):

    def __init__(self):
        Meli.__init__(self)
        self.store = Store()

    def scan_seller(self, seller_id):
        path = f'/sites/MCO/search'
        params = {
            'seller_id' : seller_id
        }
        result = self.get(path, params)
        if not result:
            return []
        total = result['paging']['total'] if result['paging']['total'] <= 1000 else 1000
        limit = result['paging']['limit']
        seller_draw = result['seller']
        products_draw = result['results']

        list_params = [{
            'seller_id' : seller_id,
            'offset' : offset,
            'limit':50,
            'attributes': 'results'
        }for offset in range(limit,total,limit)]
        products_api = self.map_pool_get(
            paths=[path]*len(list_params),
            params=list_params
        )
        for product in products_api:
            products_draw += product['results']

        seller = Seller.objects.get(
            id=seller_draw['id'])

        seller.nickname = seller_draw['nickname']
        seller.save()

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
                quantity=product_['available_quantity']
            )
            if type(product) != tuple:
                ids_products.append(product_['id'])
                for _attribute in product_['attributes']:
                    if _attribute['value_name']:
                        bulk_mgr.add(Attribute(
                            id_meli=_attribute['id'],
                            value=_attribute['value_name'],
                            product=product
                        ))
        bulk_mgr.done()

        return ids_products


    def scan_product(self, list_ids):
        path = '/items'
        params = [{
            'ids': ids,
            'attributes': 'id,pictures',
        } for ids in self.split_ids(list_ids)]

        result_draw = self.map_pool_get(
            [path]*len(params),
            params
        )

        results = list()
        for result in result_draw:
            results += result
        products_draw = {product['body']['id']:product for product in results}

        products = Product.objects.filter(sku__in=products_draw.keys())

        bulk_mgr = BulkCreateManager()
        for product in products:
            sku = product.provider_sku

            for image in products_draw[sku]['body']['pictures']:
                picture = Picture(
                    src=image['secure_url'],
                    product=product
                )
                bulk_mgr.add(picture)
        bulk_mgr.done()

class ScraperCategory(Meli):

    def __init__(self):
        Meli.__init__(self)
        self._ids = list()
        self._categories = dict()

    @property
    def ids(self):
        if not self._categories:
            for category in Category.objects.all():
                self._categories[category.id] = category
                self._ids.append(category.id)

        return self._ids

    @property
    def array(self):
        if not self._categories:
            for category in Category.objects.all():
                self._categories[category.id] = category
                self._ids.append(category.id)

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
    
    def update(self, id):
        if not int(id[3:]) in self.ids:
            path = f'/categories/{id}'
            result = self.get(path)
            name = result['name']
            father = result['path_from_root'][0]['id']
            if int(father[3:]) != int(id[3:]):
                self.update(father)
            self._set_array(id,father,name)