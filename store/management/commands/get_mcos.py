from django.core.management.base import BaseCommand, CommandError
from meli_sdk.views import get_mcos
from concurrent.futures import Future
import csv
from datetime import datetime

class Command(BaseCommand):
    help = 'Recibe por parametro el id de las categoria de MELI Colombia \
para jalar la data a nuestro MarketPlace'

    def add_arguments(self,parser):
        parser.add_argument('categories_id', nargs='+', type=str)

    def handle(self, *args, **options):
        categories_id = options['categories_id']
        for category_id in categories_id:
            mcos = get_mcos(category_id)
            print(f'{category_id} --> {len(mcos)}')
            with open(f'csv/{category_id}.csv', 'w', newline='') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=','
                                    ,quoting=csv.QUOTE_MINIMAL)
                for mco in mcos:
                    spamwriter.writerow([mco])