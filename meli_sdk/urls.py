from django.urls import path

from . import views

urlpatterns = [
    path('login', views.login, name='meli_sdk.login'),
    path('auth', views.get_token, name='meli_sdk.login')
]