from django.db import models


class Stock(models.Model):
    windcode = models.CharField(max_length=10, unique=True, verbose_name="证券代码")

    class Meta:
        db_table = 't_ff_stocks'
        verbose_name = "股票列表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.windcode
