from django.core.management.base import BaseCommand, CommandError
import csv
from store.products.views import filter_bad_products

class Command(BaseCommand):
    help = 'Deshabilitar produtos que continene malas Palabras'

    def add_arguments(self, parser):
        parser.add_argument('--seller_id', type=int)

    def handle(self, *args, **options):
        seller_id = options['seller_id']
        filter_bad_products(seller_id)