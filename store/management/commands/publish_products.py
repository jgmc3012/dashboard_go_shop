from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from store.products.models import ProductForStore
from store.products.views import filter_bad_products 
from store.store import Store
import logging
from datetime import datetime

class Command(BaseCommand):
    help = 'Despausa [limit] productos en las cuenta de mercado libre de [seller_id]'

    def add_arguments(self, parser):
        parser.add_argument('--seller_id', type=int)
        parser.add_argument('--limit', type=int, default=1000)

    def handle(self, *args, **options):
        limit = options['limit']
        seller_id = options['seller_id']
        start = datetime.now()
        logging.getLogger('log_three').info('Aplicando filtro de malas palabras a productos')
        filter_bad_products()
        logging.getLogger('log_three').info('Filtrado completado, tiempo de ejecucion {:.2f} seg'.format((datetime.now()-start).total_seconds()))

        store = Store(seller_id=seller_id)
        start = datetime.now()
        logging.getLogger('log_three').info('Consultando la base de datos')
        products = Product.objects.exclude(sku=None).filter(
            product__quantity__gt=0,
            product__available=True,
            status=ProductForStore.PAUSED,
            sale_price__gt=0,
            store_id=seller_id)[:limit]
        logging.getLogger('log_three').info('Fin de la consulta, tiempo de ejecucion {:.2f} seg'.format((datetime.now()-start).total_seconds()))
        ids = products.values_list('sku', flat=True)
        total = products.count()
        results = store.update_items(ids, [{'status': 'active'}]*total)

        posts_active = list()
        for product in results:
            if product.get('status') == 'active':
                posts_active.append(product['id'])
            else:
                logging.getLogger('log_three').warning(f'Producto no actualizado: {product}')

        ProductForStore.objects.filter(sku__in=posts_active).update(
            status=ProductForStore.ACTIVE
        )
        logging.getLogger('log_three').info(f"{len(posts_active)} Productos activados.")
        