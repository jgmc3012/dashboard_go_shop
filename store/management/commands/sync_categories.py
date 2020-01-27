from django.core.management.base import BaseCommand, CommandError
from store.products.models import Category
from meli_sdk.models import BulkCreateManager
from meli_sdk.sdk.meli import Meli

class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        bulk_mgr = BulkCreateManager()
        meli = Meli()

        path = '/sites/MLV/categories'
        result = get.(path)
        for category_draw in result:
            category = Category(
                id=category_draw['id'][3:]
                name=category_draw['name']
            )
        bulk_mgr.done()