from django.db import models
from store.models import Seller, BusinessModel
from django.utils import timezone

class Category(models.Model):
    id_meli = models.PositiveIntegerField(
        help_text="Identificador unico de la categoria en mercadolibre sin el prefijo MLV,MCO,MCL,etc",
        unique=True,
        null=True
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        related_name="category_parent"
    )
    approved = models.BooleanField(default=False)
    name = models.CharField(max_length=60)
    bad_category = models.BooleanField(default=False)
    root = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        related_name="category_root"
    )
    leaf = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.id_meli}:{self.name}'

class Product(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, null= True)
    title = models.CharField(max_length=300)
    cost_price = models.FloatField(null=True)
    ship_price = models.FloatField(null=True)
    provider_sku = models.CharField(max_length=50, unique=True)
    provider_link = models.CharField(max_length=255, unique=True)
    image = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    category_name = models.CharField(max_length=60) #"Temporal. Para el scraper de amazon"
    description = models.TextField(null=True, default=None)
    available = models.BooleanField(default=True)
    quantity = models.IntegerField()
    last_update = models.DateTimeField(default=timezone.localtime)
    modifiable = models.BooleanField(default=True)
    height = models.FloatField(default=None, null=True)
    width = models.FloatField(default=None, null=True)
    length = models.FloatField(default=None, null=True)
    weight = models.FloatField(default=None, null=True)

    def __str__(self):
        return self.title

class Picture(models.Model):
    src =  models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

class Attribute(models.Model):
    id_meli = models.CharField(max_length=50)
    value = models.CharField(max_length=350)
    value_id = models.CharField(max_length=50, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.id_meli

class ProductForStore(models.Model):
    PAUSED = 0
    ACTIVE = 1
    CLOSED = 2
    INACTIVE = 3
    UNDER_REVIEW = 4
    PAYMENT_REQUIRED = 5
    STATUS_CHOICES = [
        (PAUSED, 'Pausada'),
        (ACTIVE, 'Activa'),
        (CLOSED, 'Cerrada'),
        (INACTIVE, 'Inactiva'),
        (UNDER_REVIEW, 'Bajo revision'),
        (PAYMENT_REQUIRED, 'Pago Requerido'),
    ]
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=PAUSED
    )
    seller = models.ForeignKey(BusinessModel, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    no_problem = models.BooleanField(default=False)
    sku = models.CharField(max_length=20, unique=True)

    @property
    def store_link(self):
        return f'https://articulo.mercadolibre.com.ve/{self.sku[:3]}-{self.sku[3:]}-colchon-inflable-queen-coleman-bomba-inflador-de-pie-_JM'