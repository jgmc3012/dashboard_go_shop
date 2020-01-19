from django.urls import path

from .views import OrderView

urlpatterns = [
    path('api/new_pay/<int:order_id>', OrderView().new_pay, name='store.new_order'),
    path('api/buys/done/<int:order_id>', OrderView().order_purchased, name='store.orders.buy_done'),
    path('api/provider_deliveries/<int:order_id>', OrderView().provider_deliveries, name='store.provider_deliveries'),
    path('api/complete_order/<int:order_id>', OrderView().complete_order, name='store.complete_order'),
]