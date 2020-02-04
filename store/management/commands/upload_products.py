from django.core.management.base import BaseCommand, CommandError

from store.products.models import Product
from store.products.views import filter_bad_products 
from store.store import Store
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import logging

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
        products = Product.objects.filter(sku=None,quantity__gt=0,available=1)
        logging.info(f'Fin de la consulta, tiempo de ejecucion {datetime.now()-start}')

        store = Store()
        total = len(products)
        slices = 100
        for lap, _products in enumerate(chunks(products, slices)):
            logging.info(f'PUBLICACIONES {(lap+1)*100}/{total}')
            with ThreadPoolExecutor(max_workers=5) as executor:
                executor.map(store.publish, _products)