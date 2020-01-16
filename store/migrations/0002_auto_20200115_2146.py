# Generated by Django 3.0.1 on 2020-01-16 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='email',
            field=models.EmailField(default=None, max_length=70),
        ),
        migrations.AlterField(
            model_name='buyer',
            name='phone',
            field=models.PositiveIntegerField(default=None),
        ),
        migrations.AlterField(
            model_name='order',
            name='state',
            field=models.IntegerField(choices=[(0, 'Ofertado en MercadoLibre'), (1, 'Pagado'), (2, 'Procesando'), (3, 'Recibido en Bodega'), (4, 'Salida internacional'), (5, 'Recivido en Tienda'), (6, 'Completado')], default=0),
        ),
    ]
