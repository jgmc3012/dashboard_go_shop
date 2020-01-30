from django.core.management.base import BaseCommand, CommandError

from meli_sdk.views import update_produtcs

from dollar_for_life.models import History
from store.products.models import Product
from store.models import BusinessModel
from store.store import Store

class Command(BaseCommand):
    help = 'Actualiza los precios de la tienda en linea al cambio de la tasa actual de dolar'

    def handle(self, *args, **options):
        store = Store()
        USD = History.objects.order_by('-datetime').first()
        BM = BusinessModel.objects.get(pk=store.SELLER_ID)
        price_usd = USD.rate + BM.usd_variation

        products = Product.objects.exclude(sale_price=0,sku=None)

        ids = list()
        bodys= list()
        for product in products:
            ids.append(product.sku)
            bodys.append({
            'price': products.sale_price*price_usd
            })

        store.update_items(ids,bodys)