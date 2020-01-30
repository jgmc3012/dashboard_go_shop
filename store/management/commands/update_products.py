from django.core.management.base import BaseCommand, CommandError

from store.products.models import Product
from meli_sdk.sdk.scraper import Scraper

class Command(BaseCommand):
    help = 'Publica nuevos producto en las cuenta de mercado libre'

    def handle(self, *args, **options):
        products = Product.objects.all()

        Scraper().update_products(products)