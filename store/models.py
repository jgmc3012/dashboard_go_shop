from django.db import models


class Seller(models.Model):
    nickname = models.CharField(max_length=60, unique=True, null=True)
    id = models.PositiveIntegerField(
        help_text="Identificador unico del vendedor en la WEB/API del proveeedor",
        primary_key=True
    )
    bad_seller = models.BooleanField(default=False)

class BusinessModel(models.Model):
    """
    Aqui esta todas las variables que se le aplicaran a cada precio de costo por producto
    """
    seller_id = models.CharField(
        max_length=50,
        primary_key=True,
        help_text="Identificador unico del vendedor en la WEB/API del proveeedor",
    )
    trm = models.IntegerField(
        help_text="Conversion de la moneda del proveedor a 1 USD.",
    )
    shipping_vzla = models.IntegerField(
        help_text="Costo MAXIMO de envio dentro de venezuela(en USD).",
    )
    meli_tax = models.IntegerField(
        help_text="PORCENTAJE de la comision de mercadolibre.",
    )
    utility = models.IntegerField(
        help_text="PORCENTAJE de la utilidad de los socios.",
    )

    usd_variation = models.IntegerField(
        help_text="Precio de actualizacion del USD por encima de la taza.",
        default=10000
    )

class Buyer(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    nickname= models.CharField(max_length=30)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.PositiveIntegerField(default=None)
    email = models.EmailField(max_length=70, null=True)