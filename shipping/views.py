from django.shortcuts import render
from django.utils import timezone

from .models import Shipping,Shipper


def new_shipping(guide:int, amount:int, shipper_name:str, destination:str):
    shipper = Shipper.objects.filter(nickname=shipper_name).first()
    if not shipper:
        return {
            'ok': False,
            'msg': 'La trasportadora no esta registra.'
        }
    shipping = Shipping.objects.filter(guide=guide).first()
    if shipping:
        return {
            'ok': False,
            'msg': 'Ya hay un envio registrado con ese numero de guia.'
        }
    shipping = Shipping.objects.create(
        date_send=timezone.now(),
        amount=amount,
        guide=guide,
        shipper=shipper,
        destination=destination
    )
    return {
            'ok': True,
            'msg': 'Envio registrado',
            'data': shipping
    }

def shipment_completed(guide:int):
    shipping = Shipping.objects.filter(guide=guide).first()
    if not shipping:
        return {
            'ok': False,
            'msg': 'No existe ningun envio con esa numero de guia.'
        }
    if shipping.date_completed:
        return {
            'ok': False,
            'msg': 'La recepcion de este paquete ya fue registrada.'
        }

    shipping.date_completed=timezone.now()
    shipping.state = Shipping.COMPLETED
    shipping.save()
    return {
            'ok': True,
            'msg': '',
            'data': shipping
    }
