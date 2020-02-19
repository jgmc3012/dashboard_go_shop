from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User
from store.models import Buyer
from store.products.models import Product
from shipping.models import Shipping

from store.store import Store


class Pay(models.Model):
    amount = models.FloatField()
    reference = models.BigIntegerField(unique=True, null=True, default=None)
    confirmed = models.BooleanField(default=False)

class Invoice(models.Model):
    pay = models.OneToOneField(Pay, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None)
    date = models.DateField(default=None, null=True)

class Order(models.Model):
    CANCELLED = -1
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
        (RECEIVED_STORE, 'Recibido en Tienda'),
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

    def next_state(self):
        self.state += 1
        if self.state <= self.COMPLETED:
            return Order.get_state_display(self)
        else:
            return 'Orden completada'

class New(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    message = models.CharField(max_length=255)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.localtime)

class FeedBack(models.Model):
    REASON_MELI = {
        0:'SELLER_OUT_OF_STOCK',
        1:'SELLER_DIDNT_TRY_TO_CONTACT_BUYER',
        2:'BUYER_NOT_ENOUGH_MONEY',
        3:'BUYER_REGRETS'
    }
    SELLER_OUT_OF_STOCK = 0
    SELLER_DIDNT_TRY_TO_CONTACT_BUYER = 1
    BUYER_NOT_ENOUGH_MONEY = 2
    BUYER_REGRETS = 3
    REASON_CHOICES = [
        (SELLER_OUT_OF_STOCK, 'Me quede sin stock.'),
        (SELLER_DIDNT_TRY_TO_CONTACT_BUYER, 'No pude contactar al comprador.'),
        (BUYER_NOT_ENOUGH_MONEY, 'El Comprador no tenia suficiente dinero.'),
        (BUYER_REGRETS, 'El comprador decidio no comprar.')
        ]

    RATING_MELI = {
        -1:'negative',
        0:'neutral',
        1:'positive'
    }
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1
    RATING_CHOICES = [
        (NEGATIVE, 'Negativo.'),
        (NEUTRAL, 'Neutral.'),
        (POSITIVE, 'Positivo.')
        ]

    raiting  = models.IntegerField(choices=RATING_CHOICES)
    reason = models.IntegerField(choices=REASON_CHOICES, null=True)
    fulfilled = models.BooleanField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    message = models.CharField(max_length=159)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.localtime)