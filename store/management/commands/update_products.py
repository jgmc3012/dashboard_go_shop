from django.core.management.base import BaseCommand, CommandError

from store.products.models import Product
from meli_sdk.sdk.scraper import Scraper

class Command(BaseCommand):
    help = 'Publica nuevos producto en las cuenta de mercado libre'

    def handle(self, *args, **options):
        products = Product.objects.filter(available=True)
        scraper = Scraper()
        total = products.count()
        for lap, _products in enumerate(scraper.chunks(products, 200)):
            logging.info(f'PUBLICACIONES {(lap+1)*200}/{total}')
            scraper.update_products(_products)