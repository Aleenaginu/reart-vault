# Generated by Django 5.0.6 on 2025-02-05 09:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0002_remove_deliverypartner_is_verified_and_more'),
        ('shop', '0007_remove_shippingaddress_country_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(blank=True, choices=[('AVAILABLE', '🟢 Available'), ('REVIEWING', '🟡 Being Reviewed'), ('ASSIGNED', '🔴 Assigned'), ('PICKING_UP', 'Picking Up'), ('PICKED_UP', 'Picked Up'), ('IN_TRANSIT', 'In Transit'), ('DELIVERED', 'Delivered'), ('CANCELLED', 'Cancelled')], default='AVAILABLE', max_length=20, null=True)),
                ('delivery_pincode', models.CharField(blank=True, max_length=6, null=True)),
                ('lock_timestamp', models.DateTimeField(blank=True, null=True)),
                ('artist_address', models.TextField()),
                ('artist_pincode', models.CharField(max_length=6)),
                ('pickup_date', models.DateField()),
                ('pickup_time', models.TimeField()),
                ('pickup_notes', models.TextField(blank=True, null=True)),
                ('pickup_confirmation', models.BooleanField(default=False)),
                ('customer_address', models.TextField()),
                ('customer_pincode', models.CharField(max_length=6)),
                ('expected_delivery_date', models.DateField()),
                ('delivery_time', models.TimeField(blank=True, null=True)),
                ('delivery_notes', models.TextField(blank=True, null=True)),
                ('delivery_confirmation', models.BooleanField(default=False)),
                ('customer_signature', models.ImageField(blank=True, null=True, upload_to='signatures/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('delivery_partner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='delivery.deliverypartner')),
                ('locked_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='locked_orders', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='delivery_orders', to='shop.order')),
            ],
        ),
        migrations.CreateModel(
            name='DeliveryStatusUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('AVAILABLE', '🟢 Available'), ('REVIEWING', '🟡 Being Reviewed'), ('ASSIGNED', '🔴 Assigned'), ('PICKING_UP', 'Picking Up'), ('PICKED_UP', 'Picked Up'), ('IN_TRANSIT', 'In Transit'), ('DELIVERED', 'Delivered'), ('CANCELLED', 'Cancelled')], max_length=20)),
                ('notes', models.TextField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('delivery_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_updates', to='delivery.deliveryorder')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
