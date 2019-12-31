from django.core.management.base import BaseCommand, CommandError
from meli_sdk.views import update_produtcs
from datetime import datetime
import csv


class Command(BaseCommand):
    help = 'Crea un CSV con el MLV y el MCO de cada producto'

    def add_arguments(self,parser):
            parser.add_argument('priceUSD', type=float)

    def handle(self, *args, **options):
        start = datetime.now()

        price_usd = options['priceUSD']

        with open(f'csv/products.csv', 'r') as csvfile:
            products_draw = list(csv.reader(csvfile, delimiter=','))
            products = [{
                'mlv': product[0],
                'mco': product[1],
                # 'cost':product[2], Este es el costo para nosotros del producto
                'price': (float(product[3])*price_usd)
            }for product in products_draw]
        
        update_produtcs(products)

        print(f'Tiempo total {datetime.now()-start}')