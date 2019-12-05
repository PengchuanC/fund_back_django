from django.db import models

from api.models import Fund


class Brinson(models.Model):
    windcode = models.ForeignKey(Fund, to_field="windcode", on_delete=models.CASCADE)
    industry_code = models.CharField(max_length=2, null=True, verbose_name="行业代码")
    industry_name = models.CharField(max_length=4, null=True, verbose_name="行业简称")
    q1 = models.FloatField(null=True)
    q2 = models.FloatField(null=True)
    q3 = models.FloatField(null=True)
    q4 = models.FloatField(null=True)
    raa = models.FloatField(null=True)
    rss = models.FloatField(null=True)
    rin = models.FloatField(null=True)
    rto = models.FloatField(null=True)
    freq = models.CharField(max_length=2, default="S", verbose_name="单期/多期")
    benchmark = models.CharField(max_length=12)
    rpt_date = models.DateField(verbose_name="报告期")

    class Meta:
        db_table = "t_ff_brinson"
        verbose_name = "业绩归因(Brinson)"
        verbose_name_plural = verbose_name
