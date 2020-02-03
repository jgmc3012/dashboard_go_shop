# Generated by Django 3.0.1 on 2020-02-02 15:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('store', '0024_auto_20200202_1145'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.localtime)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('text', models.CharField(max_length=255)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.localtime)),
                ('answer', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='questions.Answer')),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.Buyer')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.Product')),
            ],
        ),
    ]