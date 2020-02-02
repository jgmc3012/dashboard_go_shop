from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User
from store.models import Buyer
from store.products.models import Product


class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    created_date = models.DateTimeField(default=timezone.localtime)

class Question(models.Model):
    id = models.BigAutoField(primary_key=True)
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    date_created = models.DateTimeField(default=timezone.localtime)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    answer = models.OneToOneField(Answer, on_delete=models.SET_NULL, null=True)