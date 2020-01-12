from django.shortcuts import render, redirect
from django.http import HttpResponse
from store.store import Store

def login(request):
    store = Store()
    url = store.auth_url()
    return redirect(url)

def get_token(request):
    query = request.GET
    store = Store()
    code = query.get('code')
    store.authorize(code, 'http://localhost:8000/store/auth')
    return HttpResponse('Autenticacion Exitosa!')
