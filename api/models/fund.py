from django.db import models


class Fund(models.Model):
    windcode = models.CharField(max_length=12, unique=True, verbose_name="证券代码")
    category = models.IntegerField(choices=((1, "公募基金"), (2, "私募基金"), (3, "银行理财")), verbose_name="证券类别")

    class Meta:
        db_table = 't_ff_funds'
        verbose_name = "基金列表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.windcode


class FundNav(models.Model):
    windcode = models.ForeignKey(Fund, to_field="windcode", on_delete=models.CASCADE)
    nav = models.FloatField(null=True, verbose_name="净值")
    nav_adj = models.FloatField(null=True, verbose_name="复权净值")
    date = models.DateField(verbose_name="净值日期")

    class Meta:
        db_table = "t_ff_fund_nav"
        verbose_name = "基金净值"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.windcode} - {self.date.strftime('%Y-%m-%d')}"
