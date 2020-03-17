from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Product
from meli_sdk.models import BulkCreateManager
from store.products.models import Product, ProductForStore
from store.models import Seller, BadWord
import re
from store.store import Store
import logging

@login_required
def get_url_product(request, sku):
    sku = sku.replace('-', '').upper()
    if sku[:3] == 'MCO':
        product = Product.objects.filter(provider_sku=sku).first()
        if not product:
            return JsonResponse({
                'ok': False,
                'msg': f'No se encontro ningun producto con el sku: {sku}'
            })
        return JsonResponse({
                'ok': True,
                'msg': 'El enlace a la publicacion del producto se abrira en una nueva ventana.',
                'data': {
                    'provider_url': product.store_link
                }
            })

    elif sku[:3] == 'MLV':
        product = Product.objects.filter(sku=sku).first()
        if not product:
            return JsonResponse({
                'ok': False,
                'msg': f'No se encontro ningun producto con el sku: {sku}'
            })
        return JsonResponse({
                'ok': True,
                'msg': 'El enlace a la publicacion del producto se abrira en una nueva ventana.',
                'data': {
                    'provider_url': product.provider_link
                }
            })

def filter_bad_words(bad_words, text):
    for _text_ in text.split():
        if (_text_.strip().upper() in bad_words) or (
            f'{_text_.strip().upper()}S' in bad_words) or (
            f'{_text_.strip().upper()}ES' in bad_words
        ):
            return _text_
    return None

def filter_bad_products(seller_id:int):
    bulk_mgr = BulkCreateManager(1000)
    products = Product.objects.filter(available=True).select_related('seller')
    bad_words = set(BadWord.objects.all().values_list('word', flat=True))
    store = Store(seller_id=seller_id)
    for product in products:
        msg = ''
        _bad_seller_ = product.seller.bad_seller if product.seller else False
        if _bad_seller_:
            msg = f'{product.provider_sku}:{product}. Es del vendedor {product.seller.id} que esta en la lista de malos vendedores.'
        else:
            match = filter_bad_words(bad_words, product.title.upper())
            if match:
                msg = f'{product.provider_sku}:{product}. Contiene palabras prohibidas. {match}'
        if msg:
            logging.warning(msg)
            product.available = False
            bulk_mgr.update(product, {'available'})
    
    bulk_mgr.done()

    products_stop = ProductForStore.objects.filter(
        status=ProductForStore.ACTIVE,
        product__available=False
    )
    results = store.publications_pauser(products_stop.values_list('sku',flat=True))

    posts_stop = list()
    for product in results:
        if product.get('status') == 'paused':
            posts_stop.append(product['id'])
        else:
            logging.warning(f'Producto no actualizado: {product}')

    ProductForStore.objects.filter(sku__in=posts_stop).update(
        status=ProductForStore.PAUSED,
        product__no_problem=False,
    )
    logging.info(f"{len(posts_stop)} Productos pausados.")