# Generated by Django 2.2.7 on 2019-12-10 17:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_auto_20191210_1730'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='fundnav',
            index_together={('windcode', 'date')},
        ),
    ]
