from django.core.management.base import BaseCommand, CommandError

from store.products.models import Product
from store.store import Store
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import logging

class Command(BaseCommand):
    help = 'Publica nuevos producto en las cuenta de mercado libre'

    def handle(self, *args, **options):
        store = Store()
        start = datetime.now()
        logging.info('Consultando la base de datos')
        products = Product.objects.filter(sku=None,quantity__gt=2)
        logging.info(f'Fin de la consulta, tiempo de ejecucion {datetime.now()-start}')

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = executor.map(store.publish, products)