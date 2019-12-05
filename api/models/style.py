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
