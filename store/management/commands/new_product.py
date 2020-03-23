from django.core.management.base import BaseCommand, CommandError
from store.products.models import Category
from meli_sdk.sdk.scraper import Scraper
from store.store import Store
import logging

class Command(BaseCommand):
    help = 'Ingresar un nuevo producto a la tienda desde el MCO de una publicacion en meli_co'

    def add_arguments(self, parser):
        parser.add_argument('--mco', type=str)

    def handle(self, *args, **options):
        logging.getLogger('log_three').info('Este comando esta deshabilitado')
        # MCO = options['mco']
        # if not MCO.upper()[:3] == 'MCO':
        #     MCO = f'MCO{MCO}'
        # res = Scraper().new_product(MCO)
        # logging.getLogger('log_three').info(res)
        # if res.sku:
        #     logging.getLogger('log_three').info('El producto ya existe en nuestra tienda')
        # else:
        #     Store().publish(product=res, paused=False)
