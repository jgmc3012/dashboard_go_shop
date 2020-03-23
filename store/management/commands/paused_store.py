from django.core.management.base import BaseCommand, CommandError
from store.store import Store
from store.products.models import ProductForStore
import logging

class Command(BaseCommand):
    help = 'Se encarga de para jalar la data a nuestro de las tiendas nuestro vendedores nuevos'

    def add_arguments(self, parser):
        parser.add_argument('--seller_id', type=int)

    def handle(self, *args, **options):
        seller_id = options['seller_id']
        store = Store(seller_id=seller_id)
        products = ProductForStore.objects.filter(status__in=(
            ProductForStore.ACTIVE,
            ProductForStore.UNDER_REVIEW
            ))
        ids = products.values_list('sku', flat=True)
        total = len(ids)
        store.update_items(ids, [{'status':'paused'}]*total)
        products.update(status=Product.PAUSED)
        logging.getLogger('log_three').info(f'{total} Productos Pausados')