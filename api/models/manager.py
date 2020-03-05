from django.db import models

from api.models import Fund


class Manager(models.Model):
    windcode = models.OneToOneField(Fund, to_field="windcode", on_delete=models.CASCADE)
    fund_fundmanager = models.CharField(max_length=20, null=True, verbose_name="基金经理")
    fund_predfundmanager = models.TextField(null=True, verbose_name="历任基金经理")
    fund_corp_fundmanagementcompany = models.CharField(max_length=20, verbose_name="管理人")
    update_date = models.DateField(verbose_name="更新日期")

    class Meta:
        db_table = "t_ff_manager"
        verbose_name = "基金经理"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.windcode.windcode}-{self.fund_fundmanager}"


class ManagerExpand(models.Model):
    windcode = models.ForeignKey(Manager, to_field="windcode", on_delete=models.CASCADE, related_name='manager_info')
    fund_manager_totalnetasset = models.FloatField(verbose_name="管理规模")
    fund_manager_resume = models.TextField(verbose_name="简介")
    fund_manager_gender = models.CharField(max_length=2, verbose_name="性别")
    nav_periodicannualizedreturn = models.FloatField(verbose_name="年化收益")
    rank = models.IntegerField(verbose_name="顺序")
    update_date = models.DateField(verbose_name="更新日期")

    class Meta:
        db_table = "t_ff_manager_expand"
        verbose_name = "基金经理-扩展数据"
        verbose_name_plural = verbose_name
