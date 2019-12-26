from django.db import models

from api.models import Fund


class Style(models.Model):
    windcode = models.ForeignKey(Fund, to_field="windcode", on_delete=models.CASCADE)
    small_value = models.FloatField()
    small_growth = models.FloatField()
    mid_value = models.FloatField()
    mid_growth = models.FloatField()
    large_value = models.FloatField()
    large_growth = models.FloatField()
    bond = models.FloatField()
    r_square = models.FloatField()
    value_date = models.DateField()
    freq = models.CharField(max_length=2)

    class Meta:
        db_table = "t_ff_style"
        verbose_name = "风格分析"
        verbose_name_plural = verbose_name
        index_together = ['value_date', "windcode"]

    def __repr__(self):
        return f"Style-{self.windcode}"


class BondStyle(models.Model):
    windcode = models.ForeignKey(Fund, to_field="windcode", on_delete=models.CASCADE)
    short = models.FloatField(default=0, verbose_name="短期利率债")
    long = models.FloatField(default=0, verbose_name="长期利率债")
    conver = models.FloatField(default=0, verbose_name="可转债")
    cre_short = models.FloatField(default=0, verbose_name="短期信用债")
    cre_medium = models.FloatField(default=0, verbose_name="中期信用债")
    cre_long = models.FloatField(default=0, verbose_name="长期信用债")
    interest = models.FloatField(default=0, verbose_name="质押式回购")
    value_date = models.DateField()

    class Meta:
        db_table = "t_ff_style_bond"
        verbose_name = "债券型基金风格分析"
        verbose_name_plural = verbose_name
        index_together = ['value_date', "windcode"]

    def __repr__(self):
        return f"Style-{self.windcode}"
