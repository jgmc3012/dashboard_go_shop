from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from store.store import Store
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

def get_or_create_buyer(buyer_id:int):
    store = Store()
    buyer = Buyer.objects.filter(id=buyer_id).first()

    if buyer:
        return buyer

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

    logging.info(f'Nuevo Comprador registrado: {buyer.nickname}')
    return buyer