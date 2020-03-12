from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import Http404
import json

from meli_sdk.models import BulkCreateManager

from store.store import Store
from meli_sdk.sdk.scraper import Scraper
from .models import Order, Buyer, Product, Pay, Invoice, New, FeedBack
from dollar_for_life.models import History

from shipping.views import new_shipping, shipment_completed


# class OrderView(LoginRequiredMixin, View):

@login_required
def new_pay( request, order_id):
    if request.method != 'POST':
        raise Http404
    json_data=json.loads(request.body)
    pay_reference = int(json_data.get('pay_reference'))
    quantity = int(json_data.get('quantity'))

    user_name = request.user.first_name
    if not (pay_reference and quantity):
        return JsonResponse({
            'ok': False,
            'msg': f'{user_name} Haz ingresado un dato incorrecto, verifica e intenta de nuevo'
        })

    store = Store()
    params = {
        'attributes': 'date_created,buyer,order_items'
    }
    
    order = Order.objects.filter(store_order_id=order_id).select_related('product').select_related('buyer').select_related('invoice').select_related('invoice__pay').first()
    if order.state >= Order.PROCESSING:
        return JsonResponse({
            'ok': False,
            'msg': f'{user_name} ya esta orden fue procesada. Contacta con un supervisor si deseas hacer cambios en ella.'
        })

    if order.state == Order.CANCELLED:
        return JsonResponse({
            'ok': False,
            'msg': f'Esta orden ya fue concelada. No se puede modificar su estado.'
        })

    if order.invoice.user:
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
        msg = f'El producto ha subido de precio.'
        New.objects.create(
            user=request.user,
            message=msg,
            order=order
        )
        return JsonResponse({
            'ok': False,
            'msg': f'{user_name}. {msg}, Contacta con tu supervisor.',
        })

    res = store.verify_existence(product)
    if not res.get('ok'):
        New.objects.create(
            user=request.user,
            message=res.get("msg"),
            order=order
        )
        return JsonResponse({
            'ok': False,
            'msg': f'{user_name}, {res.get("msg")}',
        })

    pay = Pay.objects.filter(reference=pay_reference).first()
    if pay:
        msg = f'{user_name}. El numero de referencia de ese pago ya fue registrado anteriormente.'
        New.objects.create(
            user=store.attentive_user,
            message=msg,
            order=order
        )
        return JsonResponse({
            'ok': False,
            'msg': msg
    })

    order.invoice.pay.reference = pay_reference
    order.invoice.pay.save()

    order.quantity = quantity
    order.state = Order.PAID_OUT
    order.save()
    msg = f'Referencia de pago agregada correctamente.'
    New.objects.create(
        user=request.user,
        message=msg,
        order=order
    )

    return JsonResponse({
        'ok': True,
        'msg': f'{user_name}. {msg}'
    })

@login_required
def order_purchased( request, order_id):
    json_data=json.loads(request.body)

    user = request.user
    user_name = user.first_name

    provider_order = int(json_data.get('provider_order'))
    order = Order.objects.filter(store_order_id=order_id).select_related('invoice').first()
    if not order:
        return JsonResponse({
            'ok':False,
            'msg': f'{user_name}, ese numero de orden no existe. Verificalo. Si el error persiste, comunicate con su supervisor.'
        })

    invoice = order.invoice
    if not invoice:
        return JsonResponse({
            'ok': False,
            'msg': f'{user_name}. No pudimos encontrar el recibo asociado al pago. Por favor,\
contacta al desarrollador.'
        })

    pay = invoice.pay
    if pay.confirmed:
        return JsonResponse({
            'ok': False,
            'msg': f'{user_name}. Este pago ya fue procesado por alguien mas, Si esto es un error contacta con tu supervisor.'
        })

    invoice.user = user
    invoice.datetime = timezone.localtime()
    invoice.save()

    pay.confirmed = True
    pay.save()

    order.state=Order.PROCESSING
    order.provider_order_id = provider_order
    order.save()

    msg = 'Se cambio el estado de la orden a Procesando.'
    New.objects.create(
        user=request.user,
        message=msg,
        order=order
    )
    return JsonResponse({
            'ok':True,
            'msg': f'{user_name}, {msg}'
        })

@login_required
def provider_deliveries( request, order_id):
    user_name = request.user.first_name
    order = Order.objects.filter(provider_order_id=order_id).first()
    if not order:
        order = Order.objects.filter(store_order_id=order_id).first()
    if not order:
        return JsonResponse({
            'ok':False,
            'msg': f'{user_name}, ese numero de orden no existe. Verificalo. Si el error persiste, comunicate con su supervisor.'
        })

    order.state = Order.RECEIVED_STORAGE
    order.save()
    msg = 'Se cambio el estado a de la orden a Recibido en Bodega.'
    New.objects.create(
        user=request.user,
        message=msg,
        order=order
    )
    return JsonResponse({
            'ok':True,
            'msg': f'{user_name}. {msg}'
        })

@login_required
def shipping_of_packet( request):
    shipper = 'MRW'
    json_data=json.loads(request.body)
    orders_draw = json_data.get('orders')
    amount=json_data.get('amount')
    guide_shipping = json_data.get('guide_shipping')
    orders = Order.objects.filter(store_order_id__in=orders_draw)

    if len(orders) != len(orders_draw):
        bad_orders = set(orders_draw)
        for order in orders:
            bad_orders.discard(order.store_order_id)

        return JsonResponse({
            'ok':False,
            'msg': f'El envio {guide_shipping}. No se pudo registrar porque la(s) siguiente(s) \
ordene(s) no corresponden con nuestra base de datos. \n{bad_orders}'
        })

    destination = orders[0].destination_place
    for order in orders:
        if destination != order.destination_place:
            destination = ''
            break
    
    if not destination:
        return JsonResponse({
            'ok':False,
            'msg': f'{request.user.first_name}. La guia {guide_shipping} contiene ordenes que debian\
ser enviadas a direcciones distintas. Contacta urgentemente a un supervisor.'
        })

    request_shipping = new_shipping(guide_shipping,amount,shipper,destination)

    if not request_shipping.get('ok'):
        return JsonResponse(request_shipping)

    shipping=request_shipping.get('data')
    bulk_mgr = BulkCreateManager()
    msg = f'Paquete enviado bajo en numero de guia: {guide_shipping}'
    for orden in orders:
        order.state=Order.INTERNATIONAL_DEPARTURE
        order.shipping = shipping
        bulk_mgr.update(order,{'state','shipping'})
        New.objects.create(
            user=request.user,
            message=msg,
            order=order
        )
    
    bulk_mgr.done()

    return JsonResponse({
        'ok':True,
        'msg':f'Envio {guide_shipping}, Registrado con exito.'
    })

@login_required
def received_packet( request, order_id):
    _order = Order.objects.filter(store_order_id=order_id).select_related('shipping').first()
    if not _order:
        return JsonResponse({
            'ok':False,
            'msg': 'Error pedido no encontrado.'
        })

    shipping = _order.shipping
    result = shipment_completed(shipping)
    if not result.get('ok'):
        return JsonResponse(result)

    orders = Order.objects.filter(shipping=shipping).select_related('product')

    bulk_mgr = BulkCreateManager()
    number_products = 0
    msg = 'El paquete donde se envio el producto fue recibido.'
    for order in orders:
        New.objects.create(
            user=request.user,
            message=msg,
            order=order
        )

        order.state=Order.RECEIVED_STORE
        number_products += order.quantity
        bulk_mgr.update(order, {'state'})

    bulk_mgr.done()

    message = f'Solicitud Exitosa. El paquete contenia {number_products} producto(s).\
A continuacion se listan los numeros de pedidos con sus respectivos paquetes productos:'
    for order in orders:
        message += f'\nPedido: {order.store_order_id} -> {order.quantity} {order.product.title}.'
    return JsonResponse({
        'ok':True,
        'msg': message
    })

@login_required
def complete_order( request, order_id):
    user_name=request.user.first_name

    order = Order.objects.filter(store_order_id=order_id).first()
    if not order:
        return JsonResponse({
            'ok':False,
            'msg': 'Numero de orden invalido'
        })
    order.state = Order.COMPLETED
    order.save()
    msg = 'Entrega exitosa.'
    New.objects.create(
        user=request.user,
        message=msg,
        order=order
    )
    return JsonResponse({
            'ok':True,
            'msg': f'{user_name}. {msg}'
        })

@login_required
def cancel_order(request):
    json_data=json.loads(request.body)
    message = json_data['message']
    order_id = int(json_data['orderId'])
    reason = int(json_data['reason'])
    rating = int(json_data['rating'])
    order = Order.objects.filter(store_order_id=order_id).first()
    if not order:
        return JsonResponse({
            'ok': False,
            'msg': 'El numero de pedido no existen. Esto debe ser un error, consulte al desarrollador.'
        })
    if order.state == order.CANCELLED:
        return JsonResponse({
            'ok': False,
            'msg': f'Esta orden ya fue cancelada anteriormente.'
        })

    if order.state > Order.OFFERED:
        return JsonResponse({
            'ok': False,
            'msg': f'Esta orden ya tiene un pago registrado, no es posible cancelar la misma.'
        })

    body = {
        'fulfilled':False,
        'message':'No se pudo concretar la venta',
        'reason':FeedBack.REASON_MELI[reason],
        'rating':'neutral',
    }

    store = Store()
    res = store.post(
        path=f'/orders/{order_id}/feedback',
        body=body,
        auth=True,
    )

    if res[0] == 'Feedback already exists':
        FeedBack.objects.create(
            raiting=rating,
            reason=reason,
            fulfilled=False,
            user=request.user,
            message=message,
            order=order
        )

        order.state = Order.CANCELLED
        order.save()
        return JsonResponse({
            'ok': True,
            'msg': 'Orden cancelada correctamente.',
            'data': []
        })
    else:
        return JsonResponse({
            'ok': False,
            'msg': res,
            'data': []
        })

# class NewView(LoginRequiredMixin, View):

@login_required
def create_new(request):
    json_data=json.loads(request.body)
    msg = json_data['message']
    order_id = json_data['orderId']

    order = Order.objects.filter(id=order_id).first()
    if not order:
        return JsonResponse({
            'ok': False,
            'msg': 'El numero de pedido no existen. Esto debe ser un error, consulte al desarrollador.'
        })

    New.objects.create(
        order=order,
        message=msg.strip(),
        user=request.user,
    )

    return JsonResponse({
        'ok': True,
        'msg': 'Novedad agregada correctamente.',
        'data': []
    })

@login_required
def show_news(request):
    json_data=json.loads(request.body)
    order_id = json_data['orderId']
    order = Order.objects.filter(id=order_id).first()
    if not order:
        return JsonResponse({
            'ok': False,
            'msg': 'El numero de pedido no existe. Esto debe ser un error, consulte al desarrollador.',
            'data': {}
        })

    news_objects = New.objects.filter(order=order).select_related('user')
    news = [{
        'datetime' : new.created_date.strftime('%Y/%m/%d %H:%M'),
        'user': f'{new.user.first_name} {new.user.last_name}',
        'message': new.message
    } for new in news_objects]

    return JsonResponse({
        'ok': True,
        'msg': '',
        'data': {'news':news}
    })

@login_required
def change_product(request):
    json_data=json.loads(request.body)
    order_id = json_data['productOld']
    id_product_new = json_data['productNew'].upper()
    order = Order.objects.filter(id=order_id).selected_relative('product',flat=True).first()
    if not order:
        return JsonResponse({
            'ok': False,
            'msg': 'El numero de pedido no existe. Esto debe ser un error, consulte al desarrollador.',
            'data': {}
        })

    product_new = Product.objects.filter(provider_sku=id_product_new)

    if !(product_new):

        res = Scraper().new_product(id_product_newi)
        if not res:
        return JsonResponse({
            'ok': False,
            'msg': 'El nuevo producto no se encuentra en nestra base de datos. Rectifique el sku del proveedor',
            'data': {}
        })

    msg = f'Se cambio el producto del {order.product.provider_sku} al {product_new.provider_sku}'
    order.product = product_new
    order.save()

    New.objects.create(
        order=order,
        message=msg,
        user=request.user,
    )

    return JsonResponse({
        'ok': True,
        'msg': f'{msg} exitosamente.',
        'data': []
    })
