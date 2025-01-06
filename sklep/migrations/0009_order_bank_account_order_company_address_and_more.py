# Generated by Django 5.1.4 on 2025-01-06 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sklep', '0008_remove_order_shipping_address_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='bank_account',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='company_address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='company_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='contact',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='vat_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
