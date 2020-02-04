from django.core.management.base import BaseCommand, CommandError

from store.products.models import Product
from store.products.views import filter_bad_products 
from store.store import Store
import logging


class Command(BaseCommand):
    help = 'Despausa producto en las cuenta de mercado libre'

    def handle(self, *args, **options):
        logging.info('Aplicando filtro de malas palabras a productos')
        filter_bad_products()

        start = datetime.now()
        logging.info('Consultando la base de datos')
        products = Product.objects.exclude(sku=None).filter(quantity__gt=0,available=True, status=Product.PAUSED)[:1000]
        logging.info(f'Fin de la consulta, tiempo de ejecucion {datetime.now()-start}')

        store = Store()
        ids = products.values_list('sku', flat=True)
        total = products.count()
        body = {
            'status': 'active',
        }
        path= 'items'

        store.map_pool_put(
            [path]*total,
            [body]*total
        )
        products.update(status=Product.ACTIVE)
        logging.info(f'Se Activaron {total} articulos en la tienda')