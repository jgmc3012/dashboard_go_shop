from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.contrib.auth import authenticate

from datetime import timedelta 
import logging

from store.orders.models import Order, Buyer, Product, Invoice, Pay, New
from store.store import Store
from dollar_for_life.models import History
from store.views import get_or_create_buyer

class Command(BaseCommand):
    help = 'Sincroniza los pedido ingresados en la ultima hora'

    def handle(self, *args, **options):
        store = Store()
        now = timezone.localtime()
        last_hour = now - timedelta(hours=1)
        params = {
            'seller': store.SELLER_ID,
            'order.date_created.from': f'{last_hour.strftime("%Y-%m-%d")}T{last_hour.strftime("%H")}:00:00.000-00:00',
            'order.date_created.to': f'{now.strftime("%Y-%m-%d")}T{now.strftime("%H")}:00:00.000-00:00',
            'sort':'date_desc'
        }

        path = '/orders/search'
        orders_api_draw = store.get(path, params, auth=True)
        orders_api = orders_api_draw.get('results')
        for order_draw in orders_api:
            news_draw = list()
            offer_id = order_draw.get('id')
            buyer_api = order_draw.get('buyer')

            # REGISTRAR COMPRADOR
            buyer = get_or_create_buyer(
                int(buyer_api.get('id')),
                buyer_api
            )

            # VERIFICAR EXISTENCIA DEL PRODUCTO
            product_api = order_draw.get('order_items')[0]
            quantity = product_api['quantity']
            sku = product_api.get('item').get('id')
            product = Product.objects.filter(sku=sku).first()
            if not product:
                msg = f'El producto con sku={sku} no se encuentra en nuestra \
base de datos y fue orfertado bajo el pedido {offer_id} del comprador {buyer_api}'
                # LEVANTAR NOVEDAD
                logging.warning(msg)
                continue

            USD = History.objects.order_by('-datetime').first()
            if product.sale_price*USD.rate > product_api.get('unit_price'):
                # LEVANTAR NOVEDAD
                msg = f'El precio acortado por el producto con sku={sku} no es rentable.'
                news_draw.append(msg)
                logging.warning(msg)

            res = store.verify_existence(product)
            if not res.get('ok'):
                # LEVANTAR NOVEDAD
                msg =  f'El producto con sku={sku} esta agotado'
                news_draw.append(msg)
                logging.warning(msg)

            order = Order.objects.filter(store_order_id=offer_id)
            if order:
                break

            pay = Pay.objects.create(amount=float(product_api['unit_price']))
            invoice = Invoice.objects.create(pay=pay)
            order = Order.objects.create(
                store_order_id=offer_id,
                product=product,
                quantity=quantity,
                buyer=buyer,
                invoice=invoice
            )
            for msg in news_draw:
                New.objects.create(
                    user=store.attentive_user,
                    msg=msg
                    order=order
                )