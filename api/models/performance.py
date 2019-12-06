from django.db import models

from api.models import Fund


class FundPerformance(models.Model):
    windcode = models.ForeignKey(Fund, to_field="windcode", on_delete=models.CASCADE)
    indicator = models.CharField(max_length=20, verbose_name="指标名称")
    value = models.FloatField(null=True)
    update_date = models.DateField(verbose_name="更新日期")

    class Meta:
        db_table = "t_ff_performance"
        verbose_name = "基金近期表现"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.windcode
