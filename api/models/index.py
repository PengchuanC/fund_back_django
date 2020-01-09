from django.db import models


class Index(models.Model):
    windcode = models.CharField(max_length=20, db_index=True, unique=True, verbose_name="指数简称")
    sec_name = models.CharField(max_length=45, verbose_name="指数简称")
    launch_date = models.DateField(verbose_name="成立日期")
    kind = models.CharField(max_length=20, default="normal", verbose_name="类型")

    class Meta:
        db_table = "t_ff_index"
        verbose_name = "指数列表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.windcode


class IndexClosePrice(models.Model):
    windcode = models.ForeignKey(Index, to_field="windcode", on_delete=models.CASCADE)
    date = models.DateField()
    close = models.FloatField()

    class Meta:
        db_table = "t_ff_index_cp"
        verbose_name = "指数收盘数据"
        verbose_name_plural = verbose_name
        index_together = ['windcode', 'date']
