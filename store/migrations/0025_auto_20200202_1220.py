# Generated by Django 3.0.1 on 2020-02-02 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0024_auto_20200202_1145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buyer',
            name='nickname',
            field=models.CharField(max_length=30, null=True),
        ),
    ]