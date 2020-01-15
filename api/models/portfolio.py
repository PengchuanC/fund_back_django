from django.db import models


class Portfolio(models.Model):
    port_id = models.IntegerField(auto_created=True, unique=True, db_index=True, verbose_name="组合ID")
    port_name = models.CharField(max_length=30, verbose_name="组合名称")
    port_type = models.IntegerField(choices=[(1, "普通组合")], verbose_name="组合类型")

    class Meta:
        db_table = "t_ff_portfolio"
        verbose_name = "基金池"
        verbose_name_plural = verbose_name

    def __repr__(self):
        return self.port_name


class PortfolioExpand(models.Model):
    port_id = models.ForeignKey(Portfolio, to_field="port_id", on_delete=models.CASCADE)
    port_type = models.IntegerField(choices=[(1, "观察池"), (2, "核心池"), (3, "备投池")], verbose_name="组合类型")
    windcode = models.CharField(max_length=12, verbose_name="证券代码")
    update_date = models.DateField(verbose_name="更新日期")

    class Meta:
        db_table = "t_ff_portfolio_expand"
        verbose_name = "基金池"
        verbose_name_plural = verbose_name

    def __repr__(self):
        return self.port_id


class PortfolioObserve(models.Model):
    port_id = models.ForeignKey(Portfolio, to_field="port_id", on_delete=models.CASCADE)
    windcode = models.CharField(max_length=12, verbose_name="证券代码")
    update_date = models.DateField(verbose_name="更新日期")

    class Meta:
        db_table = "t_ff_portfolio_observe"
        verbose_name = "观察池"
        verbose_name_plural = verbose_name


class PortfolioCore(models.Model):
    port_id = models.ForeignKey(Portfolio, to_field="port_id", on_delete=models.CASCADE)
    windcode = models.CharField(max_length=12, verbose_name="证券代码")
    update_date = models.DateField(verbose_name="更新日期")

    class Meta:
        db_table = "t_ff_portfolio_core"
        verbose_name = "核心池"
        verbose_name_plural = verbose_name
