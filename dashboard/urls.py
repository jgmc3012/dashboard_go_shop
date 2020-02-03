from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='dashboard.index'),
    path('questions', views.show_questions, name='dashboard.show_questions'),
    path('shipping_packages', views.shipping_packages, name='dashboard.shipping_packages'),
]