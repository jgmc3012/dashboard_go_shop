from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import Http404
import json

from meli_sdk.models import BulkCreateManager

from store.store import Store
from .models import Order, Buyer, Product, Pay, Invoice
from dollar_for_life.models import History

from shipping.views import new_shipping, shipment_completed


class OrderView(LoginRequiredMixin, View):

    def new_pay(self, request, order_id):
        if request.method != 'POST':
            raise Http404
        json_data=json.loads(request.body)
        pay_reference = int(json_data.get('pay_reference'))
        quantity = int(json_data.get('quantity'))

        if not (pay_reference and quantity):
            return JsonResponse({
                'ok': False,
                'msg': f'{user_name} Haz ingresado un dato incorrecto, verifica e intenta de nuevo'
            })

        store = Store()
        user_name = request.user.first_name
        params = {
            'attributes': 'date_created,buyer,order_items'
        }
        
        order = Order.objects.filter(store_order_id=order_id).select_related('product').select_related('buyer').first()
        if order.state >= Order.PROCESSING:
            return JsonResponse({
                'ok': False,
                'msg': f'{user_name} ya esta orden fue procesada. Contacta con un supervisor si deseas hacer cambios en ella.'
            })

        if order.invoice:
            return JsonResponse({
                'ok': False,
                'msg': f'{user_name} ya esta orden contine un pago relacionado'
            })


        path = f'/orders/{order_id}'
        result = store.get(path,params, auth=True)
        buyer = order.buyer
        product_api = result.get('order_items')[0]
        product = order.product

        USD = History.objects.order_by('-datetime').first()
        if product.sale_price*USD.rate > product_api.get('unit_price'):
            return JsonResponse({
                'ok': False,
                'msg': f'{user_name}, el producto ha subido de precio, Contacta con tu supervisor.',
            })

        res = store.verify_existence(product)
        if not res.get('ok'):
            return JsonResponse({
                'ok': False,
                'msg': f'{user_name}, {res.get("msg")}',
            })

        pay = Pay.objects.filter(reference=pay_reference).first()
        if pay:
            return JsonResponse({
                'ok': False,
                'msg': f'{user_name}. El numero de referencia de ese pago ya fue registrado anteriormente.'
        })

        pay = Pay.objects.create(
            amount=product_api.get('unit_price'),
            reference=pay_reference
        )
        invoice = Invoice.objects.create(pay=pay)

        order.quantity = quantity
        order.invoice = invoice
        order.state = Order.PAID_OUT
        order.save()

        return JsonResponse({
            'ok': True,
            'msg': f'Orden agregada correctamente.  {user_name}.'
        })


    def validate_payment(request, pay_reference):
        user=request.user
        user_name = user.first_name
        amount = float(request.GET.get('amount'))
        pay = Pay.objects.filter(reference=pay_reference).first()
        if not pay:
            return JsonResponse({
                'ok': False,
                'msg': f'{user_name}. Este pago no esta asociado con ningun pedido en nuestra base de datos.'
            })
        if not pay.amount == amount:
            return JsonResponse({
                'ok': False,
                'msg': f'{user_name}. El monto que indicas no corresponde con el del \
    pedido en nuestra base de datos. Verificalo \n si persiste \
    el error contacta con un supervisor o con el desarrollador a cargo.'
            })

        if pay.confirmed:
            return JsonResponse({
                'ok': False,
                'msg': f'{user_name}. Este pago ya fue procesado por alguien mas, Si esto es un error contacta con tu supervisor.'
            })

        invoice = Invoice.objects.filter(pay=pay).first()
        if not invoice:
            return JsonResponse({
                'ok': False,
                'msg': f'{user_name}. No pudimos encontrar el recibo asociado al pago. Por favor,\
    contacta al desarrollador.'
            })
        

        order = Order.objects.filter(invoice=invoice).first()
        if not order:
            return JsonResponse({
                'ok': False,
                'msg': f'{user_name}. No pudimos encontrar la orden asociado al pago. Por favor,\
    contacta al desarrollador.'
            })
        invoice.user = user
        invoice.datetime = timezone.now()
        pay.confirmed = True
        pay.save()
        invoice.save()
        order.state = order.PAID_OUT
        order.save()
        return JsonResponse({
            'ok': True,
            'msg': f' {user_name}. Transaccion exitosa. La orden a pasado al departamento de compras.'
        })

    def show_orders_to_buy(request):
        orders = Order.objects.filter(state=Order.PAID_OUT).select_related('product')

        products = [{
            'img':order.product.image,
            'quantity': order.quantity,
            'sku_provider':order.product.provider_sku,
            'price': f'{order.product.cost_price} USD',
            'link': f'https://articulo.mercadolibre.com.co/{order.product.provider_sku[:3]}-{order.product.provider_sku[3:]}-carro-moto-recargables-electrico-montables-ninos-ninas-ctrl-_JM',
            'title':order.product.title,
            'order_id': order.provider_id,
            } for order in orders]
        data = {
            'products':products
        }
        return JsonResponse({
            'ok': True,
            'msg': '',
            'data': data
        })

    def order_purchased(request, order_id, provider_order):
        order = Order.objects.filter(store_order_id=order_id).first()
        if not order:
            return JsonResponse({
                'ok':False,
                'msg': f'{user_name}, ese numero de orden no existe. Verificalo. Si el error persiste, comunicate con su supervisor.'
            })

        order.provider_order_id = provider_order
        order.state=Order.PROCESSING
        order.save()
        return JsonResponse({
                'ok':True,
                'msg': f'{user_name}, Se cambio el estado a de la orden a Procesando'
            })

    def provider_deliveries(request, order_id): #Esto debe ser por lotes
        order = Order.objects.filter(provider_order_id=order_id).first()
        if not order:
            order = Order.objects.filter(store_order_id=order_id).first()
        if not order:
            return JsonResponse({
                'ok':False,
                'msg': f'{user_name}, ese numero de orden no existe. Verificalo. Si el error persiste, comunicate con su supervisor.'
            })

        order.state = Order.RECEIVED_STORE
        return JsonResponse({
                'ok':True,
                'msg': f'{user_name}, Se cambio el estado a de la orden a Recibido en Bodega'
            })

    def shipping_of_packet(request, shipper):
        shippings_draw = [{ #MANDADO POR POST
            'amount':0,
            'guide_shipping':123456,
            'orders': [
                12345,
                54321,
                2268501061,
            ]
        }]

        data = list()
        bulk_mgr = BulkCreateManager()
        for shipping_draw in shippings_draw:
            orders_draw = shipping_draw.get('orders')
            amount=shipping_draw.get('amount')
            guide = shipping_draw.get('shide_shipping')

            orders = Order.objects.filter(store_order_id__in=orders_draw)

            if len(orders) != len(orders_draw):
                bad_orders = set(orders_draw)
                for order in orders:
                    bad_orders.discard(order.store_order_id)

                data.append({
                    'ok':False,
                    'msg': f'El envio {guide}. No se pudo registrar porque la(s) siguiente(s) \
    ordene(s) no corresponden con nuestra base de datos. \n{bad_orders}'
                })
                continue
            
            destination = orders[0].destination_place
            for order in orders:
                if destination != order.destination_place:
                    destination = ''
                    break
            
            if not destination:
                data.append({
                    'ok':False,
                    'msg': f'ERROR: La guia {guide_shipping} contiene ordenes que debian\
    ser enviadas a direcciones distintas. Contacta urgentemente a un supervisor.'
                })
                continue
            
            request_shipping = new_shipping(guide_shipping,amount,shipper,destination)

            if not request_shipping.get('ok'):
                data.append(request_shipping)
                continue
            
            shipping=request_shipping.get('data')
            for orden in orders:
                order.state=Order.INTERNATIONAL_DEPARTURE,
                order.shipping = shipping
                bulk_mgr.update(order,{'state','shipping'})
            data.append({
                'ok':True,
                'msg':f'Envio {guide}, Registrado con exito.'
            })
        bulk_mgr.done()

        return JsonResponse({
            'ok': True,
            'data': data
        })

    def received_packet(request,guide_shipping):
        result = shipment_completed(guide_shipping)
        if not result.get('ok'):
            return JsonResponse(result)
        
        shipping = result.get('data')

        orders = Order.objects.filter(shipping=shipping)

        bulk_mgr = BulkCreateManager()
        for order in orders:
            order.state=Order.RECEIVED_STORE
            bulk_mgr.update(order, {'state'})

        bulk_mgr.done()

        return JsonResponse({
            'okey':True,
            'msg': 'Transaccion Exitosa'
        })

    def complete_order(request,order_id):
        user_name=request.user.first_name
        shipping = result.get('data')

        order = Order.objects.filter(store_order_id=order_id).first()
        if not order:
            return JsonResponse({
                'okey':False,
                'msg': 'Numero de orden invalido'
            })

        order.state = Order.COMPLETED
        order.save()

        return JsonResponse({
                'okey':True,
                'msg': f'Entrega exitosa.  {user_name}'
            })