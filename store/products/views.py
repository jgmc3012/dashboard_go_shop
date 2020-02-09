from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Product
from meli_sdk.models import BulkCreateManager
from store.products.models import Product
from store.models import Seller
import re
from store.store import Store
import logging

@login_required
def get_url_provider(request, sku):
    sku = sku.replace('-', '')
    product = Product.objects.filter(sku=sku).first()

    if not product:
        return JsonResponse({
            'ok': False,
            'msg': f'No se encontro ningun producto con el sku: {sku}'
        })

    return JsonResponse({
            'ok': True,
            'msg': '',
            'data': {
                'provider_url': product.provider_link
            }
        })

def filter_bad_products():
    bulk_mgr = BulkCreateManager()

    products = Product.objects.filter(available=True).select_related('seller')

    store = Store()
    for product in products:
        match = re.search(store.pattern_bad_words, product.title.upper())
        if match or product.seller.bad_seller:
            if match:
                msg = f'{product.provider_sku}:{product}. Contiene palabras prohibidas. {match.group()}'
            else:
                msg = f'{product.provider_sku}:{product}. {product.seller} que esta en la lista de malos vendedores.'
            logging.warning(msg)
            product.available = False
            bulk_mgr.update(product, {'available'})
    
    bulk_mgr.done()

    products_stop = Product.objects.filter(status=Product.ACTIVE, available=False)
    results = store.publications_pauser(products_stop.values_list('sku',flat=True))

    posts_stop = list()
    for product in results:
        if product.get('status') == 'paused':
            posts_stop.append(product['id'])
        else:
            logging.warning(f'Producto no actualizado: {product}')

    Product.objects.filter(sku__in=posts_stop).update(
        status=Product.PAUSED,
        no_problem=False,
    )
    logging.info(f"{len(posts_stop)} Productos pausados.")
    