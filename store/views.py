from django.shortcuts import render, redirect
from django.http import HttpResponse
from store.store import Store

def login(request):
    store = Store()
    url = store.auth_url()
    return redirect(url)

def get_token(request):
    query = request.GET
    code = query.get('code')
    jwt_split = code.split('-')
    seller_id = jwt_split[2]
    store = Store(seller_id)
    store.authorize(code, Store.URI_CALLBACK)
    return HttpResponse('Autenticacion Exitosa!')
