# Generated by Django 2.2.7 on 2019-12-03 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20191203_1527'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicatorforplot',
            name='prt_netasset',
            field=models.FloatField(null=True, verbose_name='净资产'),
        ),
    ]
