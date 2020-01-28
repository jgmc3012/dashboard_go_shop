from django.core.management.base import BaseCommand, CommandError
from store.models import Seller
from meli_sdk.sdk.scraper import Scraper
import logging

class Command(BaseCommand):
    help = 'Se encarga de para jalar la data a nuestro de las tiendas nuestro vendedores nuevos'

    def handle(self, *args, **options):
        sellers = Seller.objects.all()

        for index, seller in enumerate(sellers):
            logging.info(f'Scrapeando al vendedor {index+1} de {len(sellers)}')
            ids = Scraper().scan_seller(seller.id)
            Scraper().scan_product(ids)