from django.db import models

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