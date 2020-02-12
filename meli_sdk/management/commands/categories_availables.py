from django.core.management.base import BaseCommand, CommandError

import logging

from store.products.models import Category
from meli_sdk.sdk.scraper import ScraperCategory
from concurrent.futures import ThreadPoolExecutor

class Command(BaseCommand):
    help = 'Verifica cuales categorias estan disponible en la tienda de VE'

    def handle(self, *args, **options):
        categories = Category.objects.all()
        scraper = ScraperCategory()
        with ThreadPoolExecutor(max_workers=5) as executor:
            logging.info('Scaneando categorias')
            executor.map(scraper.category_test_approved, categories)