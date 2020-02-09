from django.db import models

import logging


class Token(models.Model):
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expiration = models.DateTimeField()
    seller_id = models.PositiveIntegerField(default=0)