from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User
from store.models import Buyer, Product
from shipping.models import Shipping

from store.store import Store


class News(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)

class Pay(models.Model):
    amount = models.FloatField()
    reference = models.BigIntegerField(unique=True)
    confirmed = models.BooleanField(default=False)

class Invoice(models.Model):
    pay = models.OneToOneField(Pay, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None)
    date = models.DateField(default=None, null=True)

class Order(models.Model):
    OFFERED = 0
    PAID_OUT = 1
    PROCESSING = 2
    RECEIVED_STORAGE = 3
    INTERNATIONAL_DEPARTURE = 4
    RECEIVED_STORE = 5
    COMPLETED = 6
    STATES_CHOICES = [
        (OFFERED, 'Ofertado en MercadoLibre'),
        (PAID_OUT, 'Pagado'),
        (PROCESSING, 'Procesando'),
        (RECEIVED_STORAGE, 'Recibido en Bodega'),
        (INTERNATIONAL_DEPARTURE, 'Salida internacional'),
        (RECEIVED_STORE, 'Recivido en Tienda'),
        (COMPLETED, 'Completado'),
    ]

    state = models.IntegerField(
        choices=STATES_CHOICES,
        default=OFFERED
    )
    store_order_id=models.BigIntegerField(unique=True)
    provider_order_id=models.BigIntegerField(unique=True, null=True)
    date_offer = models.DateTimeField(default=timezone.localtime)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, null=True)
    shipping = models.ForeignKey(Shipping, on_delete=models.CASCADE, null=True)
    destination_place = models.CharField(max_length=255, default=Store.DIRECTION)