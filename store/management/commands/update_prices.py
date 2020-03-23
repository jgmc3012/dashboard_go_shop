from django.core.management.base import BaseCommand, CommandError

from dollar_for_life.models import History
from store.products.models import ProductForStore
from store.models import BusinessModel
from store.store import Store

class Command(BaseCommand):
    help = 'Actualiza los precios de la tienda en linea al cambio de la tasa actual de dolar'

    def add_arguments(self, parser):
        parser.add_argument('--seller_id', type=int)

    def handle(self, *args, **options):
        seller_id = options['seller_id']
        store = Store(seller_id=seller_id)
        USD = History.objects.order_by('-datetime').first()
        BM = BusinessModel.objects.get(pk=seller_id)
        price_usd = USD.country(store.country) + BM.usd_variation

        products = ProductForStore.objects.exclude(sku=None).filter(
            status__in=[Product.ACTIVE]
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