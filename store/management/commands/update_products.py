from django.core.management.base import BaseCommand, CommandError

from store.products.models import Product
from meli_sdk.sdk.scraper import Scraper

import logging

class Command(BaseCommand):
    help = 'Publica nuevos producto en las cuenta de mercado libre'

    def handle(self, *args, **options):
        products = list(Product.objects.filter(available=True).values_list('provider_sku',flat=True))
        scraper = Scraper()
        total = len(products)
        for lap, _products in enumerate(scraper.chunks(products, 1000)):
            logging.info(f'PUBLICACIONES {(lap+1)*1000}/{total}')
            scraper.update_products(_products)