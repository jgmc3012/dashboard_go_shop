from django.core.management.base import BaseCommand, CommandError
from store.store import Store
from store.products.models import Product
import logging

class Command(BaseCommand):
    help = 'Se encarga de para jalar la data a nuestro de las tiendas nuestro vendedores nuevos'

    def handle(self, *args, **options):
        store = Store()
        products = Product.objects.exclude(sku=None).filter(status=Product.ACTIVE)
        ids = products.values_list('sku', flat=True)
        store.update_items(ids, [{'status':'paused'}]*len(ids))
        products.update(status=Product.PAUSED)
