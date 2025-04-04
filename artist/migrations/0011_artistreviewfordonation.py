# Generated by Django 5.0.6 on 2025-03-17 09:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_donors_user'),
        ('artist', '0010_pronotification'),
        ('donors', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArtistReviewForDonation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(1, '1 - Poor'), (2, '2 - Fair'), (3, '3 - Good'), (4, '4 - Very Good'), (5, '5 - Excellent')])),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews_given', to='accounts.artist')),
                ('donation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='donors.donation')),
                ('donor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='donation_reviews', to='accounts.donors')),
                ('interest_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='donors.interestrequest')),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('artist', 'donation')},
            },
        ),
    ]
