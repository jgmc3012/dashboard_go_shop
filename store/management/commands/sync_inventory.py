from django.core.management.base import BaseCommand, CommandError

from store.store import Store
from store.products.models import Product
from meli_sdk.models import BulkCreateManager
import logging
from collections import defaultdict


class Command(BaseCommand):
    help = 'Sincroniza los products de la tienda en linea con nuestra base de datos.'

    def handle(self, *args, **options):
        store = Store()
        product_pauser = list()
        products = Product.objects.exclude(sku=None).exclude(modifiable=False)
        ids = products.values_list('sku',flat=True)
        params = [{
            'ids': _ids,
            'attributes': 'status,id'
        } for _ids in store.split_ids(ids)]
        path = 'items'
        
        results = store.map_pool_get(
            [path]*len(params),
            params
        )
        posts = defaultdict(list)
        for product in results:
            if product['code'] == 200:
                if product['body']['status'] == 'closed':
                    posts['deleted'].append(product['body']['id'])
                elif product['body']['status'] == 'active':
                    posts['active'].append(product['body']['id'])
                elif product['body']['status'] == 'paused':
                    posts['paused'].append(product['body']['id'])
                elif product['body']['status'] == 'under_review':
                    posts['under_review'].append(product['body']['id'])
                elif product['body']['status'] == 'inactive':
                    posts['inactive'].append(product['body']['id'])
            else:
                logging.info(product)

        logging.info(f"{len(posts['deleted'])} Productos eliminados recientemente.")
        Product.objects.filter(sku__in=posts['deleted']).update(
            status=Product.CLOSED,
            modifiable=False
        )

        logging.info(f"{len(posts['active'])} Productos activos.")
        Product.objects.filter(sku__in=posts['active']).update(
            status=Product.ACTIVE
        )

        logging.info(f"{len(posts['paused'])} Productos pausados.")
        Product.objects.filter(sku__in=posts['paused']).update(
            status=Product.PAUSED
        )

        logging.info(f"{len(posts['under_review'])} Productos bajo revision de ML.")
        Product.objects.filter(sku__in=posts['under_review']).update(
            status=Product.UNDER_REVIEW
        )

        logging.info(f"{len(posts['inactive'])} Productos inactivos por revision de ML.")
        Product.objects.filter(sku__in=posts['inactive']).update(
            status=Product.UNDER_REVIEW
        )