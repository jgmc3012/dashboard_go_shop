from django.urls import path

from .views import get_url_product

urlpatterns = [
    path('api/sku/<str:sku>', get_url_product, name='product.sku'),
]