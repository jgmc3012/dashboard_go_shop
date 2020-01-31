from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta 

from store.orders.models import Order, Buyer, Product
from store.store import Store
from dollar_for_life.models import History
import logging

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
            offer_id = order_draw.get('id')
            buyer_api = order_draw.get('buyer')

            # REGISTRAR COMPRADOR
            buyer = Buyer.objects.filter(id=buyer_api.get('id')).first()
            if not buyer:
                phone_draw = buyer_api.get('phone')
                phone = ''
                if phone_draw.get('area_code'):
                    phone += phone_draw.get('area_code')
                if phone_draw.get('number'):
                    phone +=phone_draw.get('number').replace('-','')
                if len(phone) > 5:
                    phone = int(phone)
                buyer = Buyer(
                    id = buyer_api.get('id'),
                    nickname = buyer_api.get('nickname'),
                    phone = phone,
                    first_name = buyer_api.get('first_name'),
                    last_name = buyer_api.get('last_name'),
                )
                buyer.save()

            # VERIFICAR EXISTENCIA DEL PRODUCTO
            product_api = order_draw.get('order_items')[0]
            quantity = product_api['quantity']
            sku = product_api.get('item').get('id')
            product = Product.objects.filter(sku=sku).first()
            if not product:
                msg = f'El producto con sku={sku} no se encuentra en nuestra base de datos y fue orfertado bajo el pedido {offer_id} del comprador buyer_api'
                # LEVANTAR NOVEDAD
                logging.warning(msg)
                continue

            USD = History.objects.order_by('-datetime').first()
            if product.sale_price*USD.rate > product_api.get('unit_price'):
                # LEVANTAR NOVEDAD
                msg = f'El precio acortado por el producto con sku={sku} no es rentable.'
                logging.warning(msg)

            res = store.verify_existence(product)
            if not res.get('ok'):
                # LEVANTAR NOVEDAD
                msg =  f'El producto con sku={sku} ha esta agotado'
                logging.warning(msg)
            
            order = Order.objects.filter(store_order_id=offer_id)
            if order:
                break
            order = Order.objects.create(
                store_order_id=offer_id,
                product=product,
                quantity=quantity,
                buyer=buyer
            )