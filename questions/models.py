from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User
from store.models import Buyer
from store.products.models import ProductForStore


class Question(models.Model):
    id = models.BigAutoField(primary_key=True)
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    text = models.CharField(max_length=2000)
    date_created = models.DateTimeField(default=timezone.localtime)
    product = models.ForeignKey(ProductForStore, on_delete=models.CASCADE)

    def from_date(self):
        from_date = f'{timezone.localtime()-self.date_created}'
        return from_date.split('.')[0]

class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=2000)
    created_date = models.DateTimeField(default=timezone.localtime)
    question = models.OneToOneField(Question, on_delete=models.SET_NULL, null=True)