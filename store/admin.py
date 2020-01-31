from django.contrib import admin

from .models import Seller, BusinessModel, BadWord


admin.site.register(Seller)
admin.site.register(BusinessModel)
admin.site.register(BadWord)