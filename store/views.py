from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from store.store import Store
from meli_sdk.sdk import meli
from store.models import BadWord, Buyer
import logging

@login_required
def login(request):
    store = Store()
    url = store.auth_url()
    return redirect(url)

@login_required
def get_token(request):
    query = request.GET
    code = query.get('code')
    jwt_split = code.split('-')
    seller_id = jwt_split[2]
    store = Store(seller_id)
    store.authorize(code, Store.URI_CALLBACK)
    return HttpResponse('Autenticacion Exitosa!')

def new_bad_word(word):
    word = word.strip().upper()
    BadWord.objects.get_or_create(word=word)

#Esto hay que pasarlo a el modulo de MELI
def get_or_create_buyer(buyer_id:int, buyer_draw=dict()):
    store = Store()
    buyer = Buyer.objects.filter(id=buyer_id).first()
    if buyer and ((not buyer_draw) or (buyer.first_name)):
        return buyer

    if not buyer_draw:
        path = '/sites/MLV/search'
        params = {
            'seller_id':buyer_id
        }
        buyer_api = store.get(path, params)
        nickname = buyer_api['seller']['nickname']
        buyer = Buyer.objects.create(
            id=buyer_id,
            nickname=nickname
        )
    else:
        phone_draw = buyer_draw.get('phone')
        phone = ''
        if phone_draw.get('area_code'):
            phone += phone_draw.get('area_code').replace(' ', '')
        if phone_draw.get('number'):
            phone +=phone_draw.get('number').replace('-','').replace(' ', '')
        if len(phone) > 5:
            phone = int(phone)
        else:
            phone = 0

        if not buyer:
            buyer = Buyer.objects.create(
                    id=buyer_id,
                    nickname=buyer_draw.get('nickname'),
                    phone=phone,
                    first_name=buyer_draw.get('first_name'),
                    last_name=buyer_draw.get('last_name'),
                )
        else:
            buyer.phone=phone
            buyer.nickname=buyer_draw.get('nickname')
            buyer.first_name=buyer_draw.get('first_name')
            buyer.last_name=buyer_draw.get('last_name')
            buyer.save()

    logging.getLogger('log_three').info(f'Comprador Actualizado/Registrado: {buyer}')

    return buyer