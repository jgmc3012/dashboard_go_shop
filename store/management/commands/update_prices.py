from django.core.management.base import BaseCommand, CommandError

from meli_sdk.views import update_produtcs

from dollar_for_life.models import History
from store.models import Product

from store.store import Store

class Command(BaseCommand):
    help = 'Actualiza los precios de la tienda en linea al cambio de la tasa actual de dolar'

    def handle(self, *args, **options):
        store = Store()
        USD = History.objects.order_by('-datetime').first()
        BM = BusinessModel.objects.get(pk=store.SELLER_ID)
        price_usd = USD.rate + BM.usd_variation

        products = Product.objects.filter(sale_price__gt=0)

        ids = list()
        bodys= list()
        for product in products:
            ids.append(product.sku)
            bodys.append({
            'status':'active',
            'price': products.sale_price*price_usd
            })

        store.uptade_items(ids,bodys)