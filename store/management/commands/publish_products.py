from django.core.management.base import BaseCommand, CommandError

from store.products.models import Product
from store.store import Store
from concurrent.futures import ThreadPoolExecutor


class Command(BaseCommand):
    help = 'Publica nuevos producto en las cuenta de mercado libre'

    def handle(self, *args, **options):
        store = Store()
        products = Product.objects.filter(sku=None)

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = executor.map(store.publish, products)