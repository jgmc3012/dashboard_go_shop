from django.db import models

class Provider(models.Model):
    nickname=models.CharField(max_length=50)
    seller_id=models.IntegerField()

class Product(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    mco = models.CharField(max_length=20)
    title = models.CharField(max_length=60)
    price = models.IntegerField()
    available_quantify= models.IntegerField(default=0)
    description = models.TextField()
    category = models.TextField()