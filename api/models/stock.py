from django.db import models


class Stock(models.Model):
    windcode = models.CharField(max_length=10, unique=True, verbose_name="证券代码")
    secuname = models.CharField(max_length=10, verbose_name="证券简称")

    class Meta:
        db_table = 't_ff_stocks'
        verbose_name = "股票列表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.windcode


class StockPerformance(models.Model):
    windcode = models.ForeignKey(Stock, to_field="windcode", on_delete=models.CASCADE)
    close = models.DecimalField(max_digits=10, decimal_places=4, null=False, verbose_name="收盘价")
    change = models.DecimalField(max_digits=18, decimal_places=4, null=False, verbose_name="涨跌幅")
    change_w = models.DecimalField(max_digits=18, decimal_places=4, null=False, verbose_name="周涨跌幅")
    change_m = models.DecimalField(max_digits=18, decimal_places=4, null=False, verbose_name="月涨跌幅")
    change_3m = models.DecimalField(max_digits=18, decimal_places=4, null=False, verbose_name="月涨跌幅")
    change_6m = models.DecimalField(max_digits=18, decimal_places=4, null=False, verbose_name="月涨跌幅")
    change_y = models.DecimalField(max_digits=18, decimal_places=4, null=False, verbose_name="月涨跌幅")
    change_ytd = models.DecimalField(max_digits=18, decimal_places=4, null=False, verbose_name="今年以来涨跌幅")
    date = models.DateField(null=False, verbose_name="交易日")

    class Meta:
        db_table = 't_ff_stock_performance'
        verbose_name = "股票表现"
        verbose_name_plural = verbose_name
        index_together = []

    def __str__(self):
        return self.windcode.windcode
