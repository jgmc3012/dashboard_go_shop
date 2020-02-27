from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import View

from store.orders.models import Order
from questions.models import Question
from store.products.models import Product
import json


@login_required
def index(request):
    return render(request,'dashboard/dashboard.html')

@login_required
def orders(request):
    state = request.GET.get('state') if request.GET.get('state') else -10
    state = int(state)
    if (state >= -1):
        orders = Order.objects.filter(state=state).select_related('product').select_related('buyer').select_related('invoice').select_related('invoice__pay')
    else:
        orders = Order.objects.all().select_related('product').select_related('buyer').select_related('invoice').select_related('invoice__pay')
    context = {
        'status_orders': Order.STATES_CHOICES,
        'orders': orders.order_by('-date_offer'),
        'selected': state
    }
    return render(request,'dashboard/adviser.orders.html', context)

@login_required
def shipping_packages(request):
    orders = Order.objects.filter(state=Order.RECEIVED_STORAGE).select_related('product').select_related('buyer').select_related('invoice').select_related('invoice__pay')
    context = {
        'orders': orders,
    }

    return render(request,'dashboard/adviser.shipping_of_packages.html', context)

@login_required
def show_questions(request):
    questions = Question.objects.filter(answer=None, product__status=Product.ACTIVE).select_related('product').select_related('buyer')
    context = {
        'questions': questions,
    }
    return render(request,'dashboard/adviser.questions.html', context)

@login_required
def claims(request):
    return render(request,'dashboard/dashboard.claims.html')

@login_required
def messages(request):
    return render(request,'dashboard/dashboard.messages.html')

@login_required
def corrections(request):
    return render(request,'dashboard/dashboard.corrections.html')

@login_required
def edit(request):
    return render(request,'dashboard/dashboard.edit.html')

@login_required
def profile(request):
    return render(request,'dashboard/dashboard.profile.html')

