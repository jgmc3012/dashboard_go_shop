from django.core.management.base import BaseCommand, CommandError

from store.products.models import Product, Picture
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

    def handle(self, *args, **options):
        logging.info('Aplicando filtro de malas palabras a productos')
        filter_bad_products()

        start = datetime.now()
        logging.info('Consultando la base de datos')
        sellers_bad = Product.objects.filter(Q(available=0)|Q(status=Product.CLOSED)).values_list('seller',flat=True)
        products = Product.objects.filter(
            sku=None,
            quantity__gt=0,
            available=True,
            category__leaf=True).exclude(seller__in=sellers_bad).select_related('category')
        logging.info(f'Fin de la consulta, tiempo de ejecucion {datetime.now()-start}')

        store = Store()
        slices = 100
        USD = History.objects.order_by('-datetime').first()
        BM = BusinessModel.objects.get(pk=store.SELLER_ID)
        price_usd = USD.rate + BM.usd_variation

        for lap, _products in enumerate(chunks(products, slices)):
            logging.info(f'PUBLICANDO {(lap)*100}-{(lap+1)*100}')
            with ThreadPoolExecutor(max_workers=3) as executor:
                response = executor.map(
                    store.publish,
                    _products,
                    [price_usd]*len(_products),
                    [False]*len(_products))
                limit_per_day = False
                for product in response:
                    if not product['ok'] and product.get('data'):
                        limit_per_day = (product['data'].get('message') ==  'daily_quota.reached')
                    if limit_per_day:
                        break
                if limit_per_day:
                        break