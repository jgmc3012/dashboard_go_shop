from django.core.management.base import BaseCommand, CommandError
from meli_sdk.views import get_mcos
from concurrent.futures import Future
import csv
from datetime import datetime

class Command(BaseCommand):
    help = 'Crea un CSV con el MLV y el MCO de cada producto'

    def add_arguments(self,parser):
            parser.add_argument('categories_id', nargs='+', type=str)

    def handle(self, *args, **options):
        start = datetime.now()
        
        categories_id = options['categories_id']
        for category_id in categories_id:
            time_parse = datetime.now()
            mcos = get_mcos(category_id)
            print(f'{category_id} --> {len(mcos)}')
            with open(f'csv/{category_id}.csv', 'w', newline='') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=','
                                    ,quoting=csv.QUOTE_MINIMAL)
                for mco in mcos:
                    spamwriter.writerow([mco])
            print(f'Tiempo de la categoria {category_id} {datetime.now()-time_parse}')

        print(f'Tiempo total {datetime.now()-start}')
        