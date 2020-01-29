from django.core.management.base import BaseCommand, CommandError

from store.products.models import Product
from store.store import Store


class Command(BaseCommand):
    help = 'Publica nuevos producto en las cuenta de mercado libre'

    def handle(self, *args, **options):
        store = Store()
        products = Product.objects.filter(available=False)

        for product in products[:50]:
            store.publish(product)