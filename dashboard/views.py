from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from store.orders.models import Order

@login_required()
def index(request):
    context = {
        'status_orders': [{
            'value': order[0],
            'name': order[1],
        }for order in Order.STATES_CHOICES],
    }
    return render(request,'dashboard/adviser.html', context)