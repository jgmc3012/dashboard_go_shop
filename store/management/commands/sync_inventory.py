from django.core.management.base import BaseCommand, CommandError

from store.store import Store
from store.products.models import ProductForStore
from meli_sdk.models import BulkCreateManager
import logging
from collections import defaultdict


class Command(BaseCommand):
    help = 'Sincroniza los products de la tienda en linea con nuestra base de datos.'

    def add_arguments(self, parser):
        parser.add_argument('--seller_id', type=int)

    def handle(self, *args, **options):
        seller_id = options['seller_id']
        store = Store(seller_id=seller_id)
        products = ProductForStore.objects.filter(store_id=seller_id).exclude(sku=None)
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
                logging.getLogger('log_three').info(product)

        logging.getLogger('log_three').info(f"{len(posts['deleted'])} Productos eliminados recientemente.")
        ProductForStore.objects.filter(sku__in=posts['deleted']).update(
            status=ProductForStore.CLOSED
        )

        logging.getLogger('log_three').info(f"{len(posts['active'])} Productos activos.")
        ProductForStore.objects.filter(sku__in=posts['active']).update(
            status=ProductForStore.ACTIVE
        )

        logging.getLogger('log_three').info(f"{len(posts['paused'])} Productos pausados.")
        ProductForStore.objects.filter(sku__in=posts['paused']).update(
            status=ProductForStore.PAUSED
        )

        logging.getLogger('log_three').info(f"{len(posts['under_review'])} Productos bajo revision de ML.")
        ProductForStore.objects.filter(sku__in=posts['under_review']).update(
            status=ProductForStore.UNDER_REVIEW
        )

        logging.getLogger('log_three').info(f"{len(posts['inactive'])} Productos inactivos por revision de ML.")
        ProductForStore.objects.filter(sku__in=posts['inactive']).update(
            status=ProductForStore.UNDER_REVIEW
        )