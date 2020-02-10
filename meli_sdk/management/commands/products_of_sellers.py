from django.core.management.base import BaseCommand, CommandError
from store.products.models import Category
from meli_sdk.sdk.scraper import Scraper
import logging

class Command(BaseCommand):
    help = 'Se encarga de para jalar la data a nuestro de las tiendas nuestro vendedores nuevos'

    def handle(self, *args, **options):
        categories = Category.objects.filter(leaf=True)
        total = len(categories)
        for index, category in enumerate(categories):
            logging.info(f'Scrapeando categoria {index+1} de {total}')
            ids = Scraper().scan_for_category(category)
            Scraper().scan_product(ids)