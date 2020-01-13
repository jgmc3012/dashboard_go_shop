from django.db import models

from django.utils import timezone


class History(models.Model):
    datetime = models.DateTimeField(default=timezone.localtime)
    rate = models.FloatField()