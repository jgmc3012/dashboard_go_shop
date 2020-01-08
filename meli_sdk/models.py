from django.db import models

class Token(models.Model):
    token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expiration = models.IntegerField()