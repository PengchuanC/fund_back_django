from django.db import models

from api.models import Stock


class Exposure(models.Model):
    windcode = models.ForeignKey(Stock, to_field="windcode", on_delete=models.CASCADE)
    date = models.DateField(verbose_name="交易日期")
    beta = models.FloatField(verbose_name="BETA")
    momentum = models.FloatField(verbose_name="动量")
    size = models.FloatField(verbose_name="市值")
    earning_yield = models.FloatField(verbose_name="盈利能力")
    residual_volatility = models.FloatField(verbose_name="残差波动率")
    growth = models.FloatField(verbose_name="成长")
    book_to_price = models.FloatField(verbose_name="账面市值比")
    leverage = models.FloatField(verbose_name="杠杆")
    liquidity = models.FloatField(verbose_name="流动性")
    nl_size = models.FloatField(verbose_name="非线性市值")

    class Meta:
        db_table = "t_ff_barra_exposure"
        verbose_name = "风格因子-因子暴露"
        verbose_name_plural = verbose_name
        index_together = ['date', "windcode"]

    def __repr__(self):
        return f"Exposure-{self.windcode.windcode}"
