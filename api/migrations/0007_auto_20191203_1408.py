# Generated by Django 2.2.7 on 2019-12-03 14:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20191203_1326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basicinfo',
            name='windcode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Fund', to_field='windcode'),
        ),
        migrations.CreateModel(
            name='Classify',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch', models.CharField(max_length=10, verbose_name='类别')),
                ('classify', models.CharField(max_length=20, verbose_name='分类')),
                ('update_date', models.DateField()),
                ('windcode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Fund', to_field='windcode')),
            ],
            options={
                'verbose_name': '公募基金分类',
                'verbose_name_plural': '公募基金分类',
                'db_table': 't_ff_classify',
            },
        ),
    ]
