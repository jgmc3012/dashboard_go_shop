from django.core.management.base import BaseCommand, CommandError

from store.store import Store
from store.models import Seller, BusinessModel
from store.products.models import Product
from meli_sdk.models import BulkCreateManager
import logging
from math import ceil


class Command(BaseCommand):
    help = 'Sincroniza los products de la tienda en linea con nuestra base de datos.'

    def handle(self, *args, **options):
        store = Store()
        product_pauser = list()
        skus = store.get_inventory_by_api()
        skus_provider_api = store.get_mcos_by_api(skus)
        product_pauser += skus_provider_api.get('bad') # No tienen el sku de proveedor
        skus_provider = skus_provider_api.get('fine')
        items = [skus_provider.get(key).get('mco').split('-')[0] for key in skus_provider.keys()]
        
        products_api_draw = store.get_product_by_api(items)
        products_api_okey = products_api_draw.get('fine')
        products_db = Product.objects.all()
        
        skus_in_db = [product.sku for product in products_db]

        products_draw = {
            'new': list(),
            'old': dict(),
        }

        for sku in skus_provider.keys():
            if (skus_provider[sku].get('mco').split('-')[0] in products_api_draw.get('bad')): # No tienen precio
                product_pauser.append(sku)
                if (sku in skus_in_db):
                    products_draw.get('old')[sku] = {
                        'sku':sku,
                        'cost_price': 0    
                    }
            else:
                product = {
                    'sku':sku,
                    'provider_sku': skus_provider[sku].get('mco'),
                    'title': products_api_okey[skus_provider[sku].get('mco').split('-')[0]].get('title'),
                    'image': products_api_okey[skus_provider[sku].get('mco').split('-')[0]].get('image'),
                    'seller_id': products_api_okey[skus_provider[sku].get('mco').split('-')[0]].get('seller_id'),
                    'cost_price': products_api_okey[skus_provider[sku].get('mco').split('-')[0]].get('price'),
                }
                if (not sku in skus_in_db):
                    products_draw.get('new').append(product.copy())
                else:
                    products_draw.get('old')[sku] = product.copy()

        sellers_ids = { product.get('seller_id') for product in products_draw.get('new') }
        sellers_for_api = store.get_seller_for_api(sellers_ids)

        sellers_in_db = Seller.objects.all()
        
        sellers_id_in_db = { seller.id for seller in sellers_in_db }
        sellers_new_draw = [seller for seller in sellers_for_api if (
            not seller.get('id') in (sellers_id_in_db)
        )]

        sellers = dict()
        bulk_mgr = BulkCreateManager()
        
        logging.info(f'Sellers nuevos registrados: {len(sellers_new_draw)}')
        for seller in sellers_new_draw:
            id = seller.get('id')
            sellers[id] = Seller(
                nickname=seller.get('nickname'),
                id=seller.get('id')
            )
            bulk_mgr.add(sellers[id])

        bulk_mgr.done()

        for seller in sellers_in_db:
            id = seller.id
            sellers[id] = seller

        BM = BusinessModel.objects.get(pk=store.SELLER_ID)
        product = list()
        for product_draw in products_draw.get('new'):
            cost_price = ceil(product_draw['cost_price']/BM.trm)
            sales_cost = ceil( (cost_price+BM.shipping_vzla)*(1+BM.meli_tax/100)*(1+BM.utility/100) )
            product = Product(
                seller=sellers[product_draw['seller_id']],
                title=product_draw.get('title'),
                cost_price=cost_price,
                sale_price= sales_cost,
                provider_sku=product_draw.get('provider_sku'),
                sku=product_draw.get('sku'),
                image=product_draw.get('image'),
            )
            bulk_mgr.add(product)

        for product in products_db:
            sku = product.sku
            cost_price = ceil(products_draw.get('old')[sku].get('cost_price')/BM.trm) if (
                products_draw.get('old')[sku].get('cost_price')) else 0
            sales_price = ceil((cost_price+BM.shipping_vzla)*(1+BM.meli_tax/100)*(1+BM.utility/100)) if (
                cost_price) else 0

            product.cost_price = cost_price
            product.sale_price = sales_price
            bulk_mgr.update(product, {'cost_price','sale_price'})

        bulk_mgr.done()

        store.publications_pauser(product_pauser)