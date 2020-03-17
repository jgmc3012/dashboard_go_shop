from django.db import models
from store.products.models import Product

class Shipper(models.Model):
    nickname = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)

class Shipping(models.Model):
    SEND = 0
    RECEIVED = 1
    COMPLETED = 2
    STATES_CHOICES = [
        (SEND, 'Enviado'),
        (RECEIVED, 'Recibido en oficinas'),
        (COMPLETED, 'Completado'),
    ]
    state = models.IntegerField(
        choices=STATES_CHOICES,
        default=SEND
    )
    date_send=models.DateTimeField()
    date_completed=models.DateTimeField(null=True)
    amount=models.FloatField(default=0)
    guide=models.BigIntegerField()
    destination=models.CharField(max_length=250)
    shipper=models.ForeignKey(Shipper, on_delete=models.CASCADE)

class ShipperInternational(models.Model):
    nickname = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)

class ShippingInternational(models.Model):
    country = models.CharField(max_length=3)
    package = models.ForeignKey(Product, on_delete=models.CASCADE)
    shipper = models.ForeignKey(ShipperInternational,on_delete=models.CASCADE)
    zipcode = models.CharField(max_length=10)
    price = models.FloatField()