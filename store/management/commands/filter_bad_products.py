from django.core.management.base import BaseCommand, CommandError
import csv
from store.products.views import filter_bad_products

class Command(BaseCommand):
    help = 'Deshabilitar produtos que continene malas Palabras'

    def handle(self, *args, **options):
        filter_bad_products()