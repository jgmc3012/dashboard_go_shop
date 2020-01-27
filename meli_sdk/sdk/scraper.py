from store.store import Store

from store.products import Product, Category, Attribute
from store.models import Seller, BusinessModel

from math import ceil

class Scraper():

    def __init__(self):
        self.store = Store()

    def scan_seller(self, seller_id):
        path = f'{self.API_ROOT_URL}/sites/MCO/search'
        params = {
            'seller_id' : seller_id
            'attributes' : 'paging,seller,results'
        }
        result = self.store.get(path, params)

        total = result['paging']['total'] if result['paging']['total'] <= 1000 else 1000
        limit = result['paging']['limit']
        seller_draw = result['seller']
        products_draw = result['results']

        list_params = [{
            'seller_id' : seller_id,
            'offset' : offset,
            'attributes': 'results'
        }for offset in range(limit,total,limit)]

        products_draw += self.map_pool_get(
            [path]*len(list_params),
            list_params
        )

        seller = Seller.objects.get(
            id=seller_draw['seller_id'])

        seller.nickname = seller_draw['nickname']
        seller.save()

        categories= list()
        categories_ids = list()
        for category in Category.objects.all():
            categories.append({
                category.id : category
            })
            categories_ids.append(category.id)
        

        BM = BusinessModel.objects.get(pk=self.store.SELLER_ID)
        bulk_mgr = BulkCreateManager()
        attributes = list()
        for product_ in products_draw:
            if (
                (not product_['shipping']['free_shipping']) or
                (not product_['condition'] == 'new') or
                (not product_['category_id'][3:] in categories_ids)
            ):
                continue
            cost_price = ceil(product_['price']/BM.trm)
            sales_cost = ceil( (cost_price+BM.shipping_vzla)*(1+BM.meli_tax/100)*(1+BM.utility/100) )
            key_category = [product['category_id']][3:]
            product = Product(
                seller=seller,
                title=product_['title'],
                cost_price=cost_price,
                sale_price= sales_cost,
                provider_sku=product_['id'],
                provider_link=product_['permalink']
                image=product_['thumbnail'].replace('http','https'),
                category = categories[key_category],
                quantity=product_['available_quantity']
            )
            bulk_mgr.add(product)

            for _attribute in product_['attributes']:
                attributes.append(Attribute(
                    id_meli=_attribute['id'],
                    value=_attribute['value_name'],
                    product=product
                ))
        bulk_mgr.done()
        for attribute in attributes:
            bulk_mgr.add(attribute)
        bulk_mgr.done()


    def scan_product(self, list_ids):
        path = '/items'
        params = [{
            'ids': ids_,
            'attributes': 'id,pictures',
        } for ids_ in list_ids]

        result += self.map_pool_get(
            [path]*len(list_params),
            list_params
        )

        products_draw = [{product['body']['id']:product} for product in result]

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