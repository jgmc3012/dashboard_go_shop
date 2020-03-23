from django.core.management.base import BaseCommand, CommandError

from store.products.models import Product, Picture, ProductForStore
from store.products.views import filter_bad_products
from store.store import Store
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import logging
from django.db.models import Q
from dollar_for_life.models import History
from store.models import BusinessModel

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

class Command(BaseCommand):
    help = 'Publica nuevos producto en las cuenta de mercado libre'

    def add_arguments(self, parser):
        parser.add_argument('--seller_id', type=int)

    def handle(self, *args, **options):
        seller_id = options['seller_id']
        logging.getLogger('log_three').info('Aplicando filtro de malas palabras a productos')
        filter_bad_products(seller_id=seller_id)

        start = datetime.now()
        logging.getLogger('log_three').info('Consultando la base de datos')
        store = Store(seller_id=seller_id)
        BM = BusinessModel.objects.get(pk=store.SELLER_ID)

        products = ProductForStore.objects.filter(
            store=BM,
            sku=None,
            product__available=True,
            product__quantity__gt=2).select_related('product')
        logging.getLogger('log_three').info(f'Fin de la consulta, tiempo de ejecucion {datetime.now()-start}')

        slices = 100
        USD = History.objects.order_by('-datetime').first()
        price_usd = USD.country(BM.country) + BM.usd_variation

        limit_per_day = False
        for lap, _products in enumerate(chunks(products, slices)):
            logging.getLogger('log_three').info(f'PUBLICANDO {(lap)*slices}-{(lap+1)*slices}')
            with ThreadPoolExecutor(max_workers=3) as executor:
                response = executor.map(
                    store.publish,
                    _products,
                    [price_usd]*len(_products))
                for product in response:
                    if not product['ok'] and product.get('data'):
                        limit_per_day = (product['data'].get('message') ==  'daily_quota.reached')
                    if limit_per_day:
                        break
                if limit_per_day:
                        break