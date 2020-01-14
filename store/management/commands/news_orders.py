from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta 

from store.orders.models import Order
from store.store import Store


class Command(BaseCommand):
    help = 'Sincroniza los pedido ingresados en la ultima hora'

    def handle(self, *args, **options):
        store = Store()
        last_hour = timezone.localtime() - timedelta(hours=1)
        breakpoint()
        params = {
            'seller': store.SELLER_ID,
            'order.date_created.from':f'{last_hour.strftime('%Y-%d-%m')}T00:00:00.000-00:00',
            'sort':'date_desc'
        }
        path = '/orders/search'
        orders_api = store.get(path, params)

        buyer_api = result.get('buyer') #OBTENER ESTE DATO

        # REGISTRAR COMPRADOR
        buyer = Buyer.objects.filter(id=buyer_api.get('id')).first()
        if not buyer:
            phone_draw = buyer_api.get('phone')
            phone = int(f"{phone_draw.get('area_code')}{phone_draw.get('number')}")
            buyer = Buyer(
                id = buyer_api.get('id'),
                nickname = buyer_api.get('nickname'),
                phone = phone,
                first_name = buyer_api.get('first_name'),
                last_name = buyer_api.get('last_name'),
            )
            buyer.save()

        # VERIFICAR EXISTENCIA DEL PRODUCTO
        product_api = result.get('order_items')[0] #OBTENER ESTE DATO
        sku = product_api.get('item').get('id')
        product = Product.objects.filter(sku=sku).first()
        if not product:
            pass # LEVANTAR NOVEDAD
            # 'msg': f'{user_name}, el producto no se encuentra en nuestra base de datos. Contacta con tu supervisor.'

        USD = History.objects.order_by('-datetime').first()
        if product.sale_price*USD > product_api.get('unit_price'):
            pass # LEVANTAR NOVEDAD
            # 'msg': f'{user_name}, el producto ha subido de precio, Contacta con tu supervisor.',

        res = store.verify_existence(product)
        if not res.get('ok'):
            pass # LEVANTAR NOVEDAD
            # 'msg': f'{user_name}, {res.get("msg")}',
        
        order = Order.objects.create(
            provider_id=offer_id,
            product=product,
            quantity=quantity,
            buyer=buyer,
            invoice=invoice
        )