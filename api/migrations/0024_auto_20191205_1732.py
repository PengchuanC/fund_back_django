# Generated by Django 2.2.7 on 2019-12-05 17:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_auto_20191205_0946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='managerexpand',
            name='windcode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='manager_info', to='api.Manager', to_field='windcode'),
        ),
    ]
