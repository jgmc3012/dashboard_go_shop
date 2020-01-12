from django.urls import path

from . import views

urlpatterns = [
    path('login', views.login, name='store.login'),
    path('auth', views.get_token, name='store.auth'),
]