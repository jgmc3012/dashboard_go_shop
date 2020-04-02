from django.core.management.base import BaseCommand, CommandError

from dollar_for_life.models import History
from store.products.models import ProductForStore
from store.models import BusinessModel
from store.store import Store

class Command(BaseCommand):
    help = 'Actualiza los precios de la tienda en linea al cambio de la tasa actual de dolar'

    def add_arguments(self, parser):
        parser.add_argument('--seller_id', type=int)
        parser.add_argument('--fields', type=str, nargs='+', default=[''])
        parser.add_argument('--only_actives', type=bool, default=True)

    def handle(self, *args, **options):
        seller_id = options['seller_id']
        fields = options['fields']
        only_actives = options['only_actives']

        store = Store(seller_id=seller_id)
        products = ProductForStore.objects.filter(store=store.business_model).exclude(sku=None).select_related('product')
        if only_actives:
            products.filter(status=ProductForStore.ACTIVE)
        else:
            products.filter(status_in=[ProductForStore.ACTIVE, ProductForStore.PAUSED])

        bodys= dict()

        if 'price' in fields:
            update_stock(products, bodys, store)
            return store.update_items(
                    list(bodys.keys()),
                    list(bodys.values())
                )

        if 'description' in fields:
            update_descriptions(products, bodys, store)
            return store.update_items(
                    list(bodys.keys()),
                    list(bodys.values())
                )

def update_stock(products:list, bodys:dict, store):
    """
    Calcula el precio de venta a la tasa local de la tienda y el stock
    """
    for product in products:
        bodys[product.sku] = {
            'price': product.sale_price*store.price_usd,
            'available_quantity': product.product.available_quantity,
        }

def update_descriptions(products:list, bodys:dict, store, inner_description=False):
    """
    Sincroniza las descriciones en MELI con las ubicadas en la DB.
        - inner_description: Espeficica si se colocara la descripcion real del
        producto dentro de la descripcion de mercadolibre.
    """
    for product in products:
        bodys[f'{product.sku}/description'] = {
            'plain_text': store.description
        }