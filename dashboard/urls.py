from django.urls import path

from .views import DashView

urlpatterns = [
    path('', DashView().index, name='dashboard.index'),
    path('questions', DashView().questions, name='dashboard.questions'),
    path('shipping_packages', DashView().shipping_packages, name='dashboard.shipping_packages'),
]