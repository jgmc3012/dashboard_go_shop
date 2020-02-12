from django.urls import path

from . import views

urlpatterns = [
    path('', views.orders, name='dashboard.index'),
    path('orders', views.orders, name='dashboard.orders'),
    path('questions', views.show_questions, name='dashboard.show_questions'),
    path('shipping_packages', views.shipping_packages, name='dashboard.shipping_packages'),
    path('claims', views.claims, name='dashboard.claims'),
    path('messages', views.messages, name='dashboard.messages'),
    path('corrections', views.corrections, name='dashboard.corrections'),
    path('edit', views.edit, name='dashboard.edit'),
    path('profile', views.profile, name='dashboard.profile'),
] 