from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import View

from store.orders.models import Order


@login_required
def index(request):
    state = request.GET.get('state') if request.GET.get('state') else -1
    state = int(state)
    if (state >= 0):
        orders = Order.objects.filter(state=state).select_related('product').select_related('buyer')
    else:
        orders = Order.objects.all().select_related('product').select_related('buyer')
    
    context = {
        'status_orders': Order.STATES_CHOICES,
        'orders': orders,
        'selected': state
    }
    return render(request,'dashboard/adviser.orders.html', context)

@login_required
def shipping_packages(request):
    orders = Order.objects.filter(state=Order.RECEIVED_STORAGE).select_related('product').select_related('buyer')
    context = {
        'orders': orders,
    }

    return render(request,'dashboard/adviser.shipping_of_packages.html', context)

@login_required
def questions(request):
    return render(request,'dashboard/adviser.questions.html')