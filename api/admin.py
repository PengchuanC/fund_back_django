from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget

from api import models


admin.site.site_header = "产品开发部后台管理系统"


class FundResource(resources.ModelResource):
    class Meta:
        model = models.Fund


@admin.register(models.Fund)
class FundAdmin(ImportExportModelAdmin):
    list_display = ('windcode', 'category')
    search_fields = ('windcode', 'category')
    resource_class = FundResource


class BasicInfoResource(resources.ModelResource):
    windcode = fields.Field(
        column_name='windcode',
        attribute='windcode',
        widget=ForeignKeyWidget(models.Fund, 'windcode')
    )

    class Meta:
        model = models.BasicInfo


@admin.register(models.BasicInfo)
class BasicInfo(ImportExportModelAdmin):
    list_display = ['windcode', 'sec_name', 'setup_date', 'company', 'first_invest_type', 'update_date']
    search_fields = ['windcode', 'sec_name']
    resource_class = BasicInfoResource


@admin.register(models.Classify)
class ClassifyAdmin(admin.ModelAdmin):
    list_display = ["windcode", "branch", "classify", "update_date"]
    search_fields = ["branch", "classify"]


class ManagerResource(resources.ModelResource):
    class Meta:
        model = models.Manager


@admin.register(models.Manager)
class ManagerAdmin(ImportExportModelAdmin):
    list_display = ["windcode", "fund_fundmanager", "fund_corp_fundmanagementcompany", "update_date"]
    resource_class = ManagerResource


@admin.register(models.ManagerExpand)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ["windcode", "fund_manager_resume"]


class PortfolioResource(resources.ModelResource):
    class Meta:
        model = models.Portfolio


@admin.register(models.Portfolio)
class PortfolioAdmin(ImportExportModelAdmin):
    list_display = ["port_id", "port_name", "port_type"]
    search_fields = ['port_name']
    resource_class = PortfolioResource


@admin.register(models.PortfolioExpand)
class PortfolioExpandAdmin(admin.ModelAdmin):
    list_display = ["port_id", "port_type", "windcode", "update_date"]
    search_fields = ['port_id', "port_type", "windcode"]


@admin.register(models.Index)
class IndexAdmin(admin.ModelAdmin):
    list_display = ['windcode', 'launch_date', 'kind']


class IndexClosePriceResource(resources.ModelResource):
    windcode = fields.Field(
        column_name='windcode',
        attribute='windcode',
        widget=ForeignKeyWidget(models.Index, 'windcode')
    )

    class Meta:
        model = models.IndexClosePrice


@admin.register(models.IndexClosePrice)
class IndexClosePriceAdmin(ImportExportModelAdmin):
    list_display = ['id', 'windcode', 'close', 'date']
    resource_class = IndexClosePriceResource


class IndicatorIndexResource(resources.ModelResource):
    windcode = fields.Field(
        column_name='windcode',
        attribute='windcode',
        widget=ForeignKeyWidget(models.Index, 'windcode')
    )

    class Meta:
        model = models.IndicatorIndex


@admin.register(models.IndicatorIndex)
class IndicatorIndexAdmin(ImportExportModelAdmin):
    list_display = ['id', 'windcode', 'indicator', 'numeric', 'text', 'note', 'rpt_date', 'update_date']
    resource_class = IndicatorIndexResource


class BasicResource(resources.ModelResource):
    windcode = fields.Field(
        column_name='windcode',
        attribute='windcode',
        widget=ForeignKeyWidget(models.Fund, 'windcode')
    )

    class Meta:
        model = models.Basic


@admin.register(models.Basic)
class BasicAdmin(ImportExportModelAdmin):
    list_display = ['id', 'windcode', 'sec_name', 'company', 'invest_type', 'scale', 'manager', 'comment']
    resources_class = BasicResource


class LabelResource(resources.ModelResource):
    windcode = fields.Field(
        column_name='windcode',
        attribute='windcode',
        widget=ForeignKeyWidget(models.Basic, 'windcode')
    )

    class Meta:
        model = models.Label


@admin.register(models.Label)
class LabelAdmin(ImportExportModelAdmin):
    list_display = ['windcode', 'label']

    resource_class = LabelResource


class FundNavResource(resources.ModelResource):
    windcode = fields.Field(
        column_name='windcode',
        attribute='windcode',
        widget=ForeignKeyWidget(models.Fund, 'windcode')
    )

    class Meta:
        model = models.FundNav


@admin.register(models.FundNav)
class FundNavAdmin(ImportExportModelAdmin):
    list_display = ['id', 'windcode', 'nav', 'nav_adj', 'date', 'revised_date']
    search_fields = ['windcode', 'date', 'revised_date']
    resource_class = FundNavResource
