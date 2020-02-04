from django.core.management.base import BaseCommand, CommandError
from store.store import Store
from store.products.models import Product
import logging

class Command(BaseCommand):
    help = 'Se encarga de para jalar la data a nuestro de las tiendas nuestro vendedores nuevos'

    def handle(self, *args, **options):
        store = Store()
        products = Product.objects.exclude(sku=None).exclude(status=Product.CLOSED)
        ids = products.values_list('sku', flat=True)
        total = len(ids)
        store.update_items(ids, [{'status':'paused'}]*total)
        products.update(status=Product.PAUSED)
        logging.info(f'{total} Productos Pausados')