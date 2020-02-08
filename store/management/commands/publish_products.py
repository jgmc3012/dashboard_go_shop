from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from store.products.models import Product
from store.products.views import filter_bad_products 
from store.store import Store
import logging
from datetime import datetime


class Command(BaseCommand):
    help = 'Despausa producto en las cuenta de mercado libre'

    def handle(self, *args, **options):
        start = datetime.now()
        logging.info('Aplicando filtro de malas palabras a productos')
        filter_bad_products()
        logging.info('Filtrado completado, tiempo de ejecucion {:.2f} seg'.format((datetime.now()-start).total_seconds()))

        start = datetime.now()
        logging.info('Consultando la base de datos')
        sellers_bad = Product.objects.filter(Q(available=0)|Q(status=Product.CLOSED)).values_list('seller',flat=True)
        products = Product.objects.exclude(sku=None).filter(quantity__gt=0,available=True, status=Product.PAUSED).exclude(seller__in=sellers_bad)[:1000]
        logging.info('Fin de la consulta, tiempo de ejecucion {:.2f} seg'.format((datetime.now()-start).total_seconds()))
        store = Store()
        ids = products.values_list('sku', flat=True)
        total = products.count()
        results = store.update_items(ids, [{'status': 'active'}]*total)

        posts_active = list()
        for product in results:
            elif product['body']['status'] == 'active':
                posts_active.append(product['body']['id'])

        Product.objects.filter(sku__in=posts['active']).update(
            status=Product.ACTIVE
        )
        logging.info(f"{len(posts_active)} Productos activados.")
        