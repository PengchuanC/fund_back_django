# Generated by Django 2.2.7 on 2019-12-02 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_auto_20191202_1455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='keyword',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
