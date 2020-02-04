from django.core.management.base import BaseCommand, CommandError

from store.store import Store
from store.models import Seller, BusinessModel
from store.products.models import Product
from meli_sdk.models import BulkCreateManager
import logging
from math import ceil


class Command(BaseCommand):
    help = 'Sincroniza los products de la tienda en linea con nuestra base de datos.'

    def handle(self, *args, **options):
        store = Store()
        product_pauser = list()
        products = Product.objects.exclude(sku=None).exclude(modifiable=False)
        ids = products.values_list('sku',flat=True)
        params = [{
            'ids': _ids,
            'attributes': 'status, id'
        } for _ids in store.split_ids(ids)]
        path = 'items'
        
        results = store.map_pool_get(
            [path]*len(params),
            params
        )
        
        posts_deleted = list()
        posts_active = list()
        for product in results:
            if product['code'] == 200:
                if product['body']['status'] == 'closed':
                    posts_deleted.append(product['body']['id'])
                elif product['body']['status'] == 'active':
                    posts_active.append(product['body']['id'])

        Product.objects.filter(sku__in=posts_deleted).update(
            status=Product.CLOSED,
            modifiable=False
        )

        Product.objects.filter(sku__in=posts_active).update(
            status=Product.ACTIVE
        )