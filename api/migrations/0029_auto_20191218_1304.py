# Generated by Django 2.2.7 on 2019-12-18 13:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_basic_label'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basic',
            name='windcode',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='basic', to='api.Fund', to_field='windcode'),
        ),
    ]
