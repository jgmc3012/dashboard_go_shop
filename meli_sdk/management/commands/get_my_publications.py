from django.core.management.base import BaseCommand, CommandError
from meli_sdk.views import get_items_for_seller, search_items, rq_products_by_id, get_prices
from concurrent.futures import Future
from datetime import datetime
import csv
from math import ceil


class Command(BaseCommand):
    help = 'Crea un CSV con el MLV y el MCO de cada producto'

    def handle(self, *args, **options):
        start = datetime.now()
        items = get_items_for_seller(503380447)
        products, products_outwith_sku = search_items(items, rq_products_by_id)
        print('---------------------------------------------------------------')
        products_with_price, products_outwith_price_draw = get_prices(products)

        TRM = 3250 # Jalar de la BD, Admin DJ
        SHIPPING = 10 #Estos son USD. Jalar de la BD, Admin DJ
        IMPUESTO_MELI = 1.16 # Jalar de la BD, Admin DJ. O Automatizar desde la API
        UTILIDAD = 1.2 # Jalar de la BD, Admin DJ

        products_outwith_price = list()

        for key in products.keys():
            product = products[key]
            if product.get('mco') in products_outwith_price_draw:
                products_outwith_price.append(product)
            else:
                product['cost'] = products_with_price[product.get('mco').split('-')[0]]
                if product.get('cost') < 70000:
                    if product.get('cost') < 30000:
                        product['price'] = ceil((product['cost']/(TRM+SHIPPING))*IMPUESTO_MELI*UTILIDAD)
                        #Pausar
                    else:
                        product['price'] = ceil((product['cost']/(TRM+SHIPPING/2))*IMPUESTO_MELI*UTILIDAD)
                else:
                    product['price'] = ceil((product['cost']/TRM+SHIPPING)*IMPUESTO_MELI*UTILIDAD)


        for product in products_outwith_price:
            del products[product.get('mlv')]

        with open(f'csv/products.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=','
                                ,quoting=csv.QUOTE_MINIMAL)
            
            for product in products.values():
                spamwriter.writerow(product.values())

        if products_outwith_sku:
            with open(f'csv/outwith_sku.csv', 'w', newline='') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=','
                                    ,quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow(products_outwith_sku)

        if products_outwith_price:
            with open(f'csv/outwith_price.csv', 'w', newline='') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=','
                                    ,quoting=csv.QUOTE_MINIMAL)
                for product in products_outwith_price:
                    spamwriter.writerow(product.values())



        print(f'Productos correctos: {len(products.values())}')
        print(f'Tiempo total {datetime.now()-start}')
        