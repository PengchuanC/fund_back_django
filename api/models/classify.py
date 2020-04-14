from django.db import models

from api.models import Fund


class Classify(models.Model):
    windcode = models.ForeignKey(Fund, to_field="windcode", on_delete=models.CASCADE)
    branch = models.CharField(max_length=10, verbose_name="类别")
    classify = models.CharField(max_length=20, verbose_name="分类")
    kind = models.CharField(max_length=20, default="normal", verbose_name="类型")
    update_date = models.DateField()

    class Meta:
        db_table = "t_ff_classify"
        verbose_name = "公募基金分类"
        verbose_name_plural = verbose_name
