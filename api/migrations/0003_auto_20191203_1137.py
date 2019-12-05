# Generated by Django 2.2.7 on 2019-12-03 11:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20191203_1114'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fund',
            options={'verbose_name': '基金列表', 'verbose_name_plural': '基金列表'},
        ),
        migrations.AlterModelOptions(
            name='fundnav',
            options={'verbose_name': '基金净值', 'verbose_name_plural': '基金净值'},
        ),
        migrations.CreateModel(
            name='BasicInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sec_name', models.CharField(max_length=30, verbose_name='简称')),
                ('fullname', models.CharField(db_column='fund_fullname', max_length=100, null=True, verbose_name='全称')),
                ('setup_date', models.DateField(db_column='fund_setupdate', verbose_name='成立日期')),
                ('benchmark', models.CharField(db_column='fund_benchmark', max_length=100, verbose_name='业绩基准')),
                ('company', models.CharField(db_column='fund_fundmanagementcompany', max_length=20, null=True, verbose_name='管理人')),
                ('invest_scope', models.TextField(db_column='fund_investscope', null=True, verbose_name='投资范围')),
                ('structured', models.IntegerField(choices=[(0, '是'), (1, '否')], db_column='fund_structuredfundornot', verbose_name='分级基金')),
                ('first_invest_type', models.CharField(db_column='fund_firstinvesttype', max_length=25, null=True, verbose_name='投资类型(一级)')),
                ('invest_type', models.CharField(db_column='fund_investtype', max_length=25, null=True, verbose_name='投资类型')),
                ('update_date', models.DateField(verbose_name='更新日期')),
                ('windcode', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.Fund')),
            ],
            options={
                'verbose_name': '基金基础信息',
                'verbose_name_plural': '基金基础信息',
            },
        ),
    ]
