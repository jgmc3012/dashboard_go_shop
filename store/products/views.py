from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Product


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