from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='dashboard.index'),
    path('orders', views.orders, name='dashboard.orders'),
    path('questions', views.show_questions, name='dashboard.show_questions'),
    path('shipping_packages', views.shipping_packages, name='dashboard.shipping_packages'),
    path('reclamos', views.reclamos, name='dashboard.reclamos'),
    path('mensajes', views.mensajes, name='dashboard.mensajes'),
    path('correccion', views.correccion, name='dashboard.correccion'),
    path('editar', views.editar, name='dashboard.editar'),
    path('perfil', views.perfil, name='dashboard.perfil'),
] 