from django.urls import path

from .views import get_url_provider

urlpatterns = [
    path('api/mlv/<str:sku>', get_url_provider, name='product.url_provider'),
]