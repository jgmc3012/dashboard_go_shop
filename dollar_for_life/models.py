from django.db import models

from django.utils import timezone


class History(models.Model):
    datetime = models.DateTimeField(default=timezone.localtime)
    ve = models.FloatField()
    do = models.FloatField()
    mx = models.FloatField()

    def country(self, country:str):
        country = country.lower()
        currencies = {
            've':self.ve,
            'do':self.do,
            'mx':self.mx,       
        }
        return currencies[country]