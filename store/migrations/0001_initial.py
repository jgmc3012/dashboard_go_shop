# Generated by Django 3.0.1 on 2020-01-14 01:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shipping', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessModel',
            fields=[
                ('seller_id', models.CharField(help_text='Identificador unico del vendedor en la WEB/API del proveeedor', max_length=50, primary_key=True, serialize=False)),
                ('trm', models.IntegerField(help_text='Conversion de la moneda del proveedor a 1 USD.')),
                ('shipping_vzla', models.IntegerField(help_text='Costo MAXIMO de envio dentro de venezuela(en USD).')),
                ('meli_tax', models.IntegerField(help_text='PORCENTAJE de la comision de mercadolibre.')),
                ('utility', models.IntegerField(help_text='PORCENTAJE de la utilidad de los socios.')),
                ('usd_variation', models.IntegerField(default=10000, help_text='Precio de actualizacion del USD por encima de la taza.')),
            ],
        ),
        migrations.CreateModel(
            name='Buyer',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('nickname', models.CharField(max_length=30)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('phone', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('reference', models.BigIntegerField(unique=True)),
                ('confirmed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('nickname', models.CharField(max_length=60, unique=True)),
                ('id', models.PositiveIntegerField(help_text='Identificador unico del vendedor en la WEB/API del proveeedor', primary_key=True, serialize=False)),
                ('bad_seller', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=60)),
                ('cost_price', models.FloatField(null=True)),
                ('sale_price', models.FloatField(null=True)),
                ('provider_sku', models.CharField(max_length=50)),
                ('sku', models.CharField(max_length=20, unique=True)),
                ('image', models.CharField(max_length=255)),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.Seller')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.IntegerField(choices=[(0, 'Ofertado en MercadoLibre'), (1, 'Pagado'), (2, 'Procesando'), (3, 'Recivido en Bodega'), (4, 'Salida internacional'), (5, 'Recivido en Tienda'), (6, 'Completado')], default=0)),
                ('store_order_id', models.PositiveIntegerField(unique=True)),
                ('provider_order_id', models.PositiveIntegerField(null=True, unique=True)),
                ('date_offer', models.DateTimeField(default=django.utils.timezone.localtime)),
                ('quantity', models.IntegerField()),
                ('destination_place', models.CharField(default='Caracas Chacaito', max_length=255)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.Buyer')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.Invoice')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.Product')),
                ('shipping', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='shipping.Shipping')),
            ],
        ),
        migrations.AddField(
            model_name='invoice',
            name='pay',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='store.Pay'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='user',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]