from django.db import models

from api.models import Fund


class Asset(models.Model):
    windcode = models.ForeignKey(Fund, to_field="windcode", on_delete=models.CASCADE)
    stock = models.FloatField(default=0.0, verbose_name="股票")
    bond = models.FloatField(default=0.0, verbose_name="债券")
    fund = models.FloatField(default=0.0, verbose_name="基金")
    warrant = models.FloatField(default=0.0, verbose_name="权证")
    cash = models.FloatField(default=0.0, verbose_name="现金")
    other = models.FloatField(default=0.0, verbose_name="其他")
    status = models.CharField(max_length=8, verbose_name="数据类型")
    date = models.DateField(verbose_name="更新时间")

    class Meta:
        db_table = "t_ff_asset"
        verbose_name = "资产配置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.windcode.windcode


class AssetIndustry(models.Model):
    windcode = models.ForeignKey(Fund, to_field="windcode", on_delete=models.CASCADE)
    industry = models.CharField(max_length=4, verbose_name="行业名称")
    rank = models.IntegerField(verbose_name="排序")
    ratio = models.FloatField(verbose_name="占比")
    change = models.FloatField(null=True, verbose_name="变化")
    date = models.DateField(verbose_name="更新时间")

    class Meta:
        db_table = "t_ff_asset_industry"
        verbose_name = "行业配置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.windcode.windcode


class StockHolding(models.Model):
    windcode = models.ForeignKey(Fund, to_field="windcode", on_delete=models.CASCADE)
    stock_code = models.CharField(max_length=12, verbose_name="股票代码")
    stock_name = models.CharField(max_length=12, verbose_name="股票简称")
    rank = models.IntegerField(verbose_name="排序")
    ratio = models.FloatField(verbose_name="占比")
    change = models.FloatField(null=True, verbose_name="变化")
    date = models.DateField(verbose_name="更新时间")

    class Meta:
        db_table = "t_ff_asset_stock"
        verbose_name = "股票配置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.stock_name


class BondHolding(models.Model):
    windcode = models.ForeignKey(Fund, to_field="windcode", on_delete=models.CASCADE)
    bond_code = models.CharField(max_length=18, verbose_name="债券代码")
    bond_name = models.CharField(max_length=20, verbose_name="债券简称")
    rank = models.IntegerField(verbose_name="排序")
    ratio = models.FloatField(verbose_name="占比")
    change = models.FloatField(null=True, verbose_name="变化")
    date = models.DateField(verbose_name="更新时间")

    class Meta:
        db_table = "t_ff_asset_bond"
        verbose_name = "股票配置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.bond_name
