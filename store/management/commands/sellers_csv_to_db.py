from django.core.management.base import BaseCommand, CommandError
import csv
from store.models import Seller
from meli_sdk.models import BulkCreateManager

class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        bulk_mgr = BulkCreateManager()
        sellers = set()
        with open(f'csv/providers.csv', 'r', newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=','
                                ,quoting=csv.QUOTE_MINIMAL)
            for seller in spamreader: 
                sellers.add(seller[0])
        
        for id in sellers:
            seller = Seller(id=id)
            bulk_mgr.add(seller)
        bulk_mgr.done()