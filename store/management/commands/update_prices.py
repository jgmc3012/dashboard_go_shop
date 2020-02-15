from django.core.management.base import BaseCommand, CommandError

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

        products = Product.objects.exclude(sku=None).filter(
            available=True,
            status__in=[Product.ACTIVE,Product.PAUSED]
        )

        ids = list()
        bodys= list()
        for product in products:
            ids.append(product.sku)
            bodys.append({
                'price': product.sale_price*price_usd,
                'available_quantity': 5 if product.quantity > 5 else product.quantity,
            })

        store.update_items(ids,bodys)