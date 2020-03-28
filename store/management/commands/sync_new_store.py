from django.core.management.base import BaseCommand, CommandError

from store.store import Store
from store.models import BusinessModel
from meli_sdk.sdk.scraper import Scraper
from store.products.models import ProductForStore
from meli_sdk.models import BulkCreateManager
from concurrent.futures import ThreadPoolExecutor

import logging


class Command(BaseCommand):
    help = 'Sincroniza los products de la tienda en linea con nuestra base de datos.'

    def add_arguments(self, parser):
        parser.add_argument('--seller_id', type=int)

    def handle(self, *args, **options):
        seller_id = options['seller_id']
        business = BusinessModel.objects.get(pk=seller_id)
        scraper = Scraper(seller_id)

        logging.getLogger('log_three').info('Iniciando Scraper')
        products_sku = set(scraper.get_items_for_store_id(seller_id))
        products_exits = ProductForStore.objects.filter(sku__in=products_sku)

        for product in products_exits:
            products_sku.remove(product.sku)

        ids = scraper.split_ids(products_sku)
        with ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(scraper.new_products, ids, [business]*len(ids))