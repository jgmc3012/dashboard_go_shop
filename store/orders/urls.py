from django.urls import path

from . import views

urlpatterns = [
    path('api/new_pay/<int:order_id>', views.new_pay, name='store.new_order'),
    path('api/buys/done/<int:order_id>', views.order_purchased, name='store.orders.buy_done'),
    path('api/provider_deliveries/<int:order_id>', views.provider_deliveries, name='store.provider_deliveries'),
    path('api/shipping_package', views.shipping_of_packet, name='store.shipping_package'),
    path('api/complete_order/<int:order_id>', views.complete_order, name='store.complete_order'),
    path('api/received_package/<int:order_id>', views.received_packet, name='store.received_package'),
    path('api/cancel',views.cancel_order, name='order.cancel'),
    path('api/news/create', views.create_new, name='store.create_new'),
    path('api/news/show', views.show_news, name='store.show_news'),
]