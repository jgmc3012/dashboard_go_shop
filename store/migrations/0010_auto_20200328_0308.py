# Generated by Django 3.0.1 on 2020-03-28 07:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_flatproduct'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productforstore',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='store.Product'),
        ),
    ]
