from django.urls import path

from . import views

urlpatterns = [
    path('api/new_order/<int:offer_id>', views.new_order, name='store.new_order'),
    path('api/pay/validate/<int:pay_reference>', views.validate_payment, name='store.validate_payment'),
    path('api/buys/to_do', views.show_orders_to_buy, name='store.orders.buys_to_do'),
    path('api/buys/done/<int:order_id>/<int:provider_order>', views.order_purchased, name='store.orders.buy_done'),
]