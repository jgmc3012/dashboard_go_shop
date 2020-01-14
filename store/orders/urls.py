from django.urls import path

from .views import OrderView

urlpatterns = [
    path('api/new_pay/<int:order_id>', OrderView().new_pay, name='store.new_order'),
    path('api/pay/validate/<int:pay_reference>', OrderView().validate_payment, name='store.validate_payment'),
    path('api/buys/to_do', OrderView().show_orders_to_buy, name='store.orders.buys_to_do'),
    path('api/buys/done/<int:order_id>/<int:provider_order>', OrderView().order_purchased, name='store.orders.buy_done'),
]