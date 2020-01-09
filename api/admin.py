from django.contrib import admin

from api import models


admin.site.site_header = "产品开发部后台管理系统"


@admin.register(models.Fund)
class FundAdmin(admin.ModelAdmin):
    list_display = ('windcode', 'category')
    search_fields = ('windcode', 'category')


@admin.register(models.FundNav)
class FundNavAdmin(admin.ModelAdmin):
    list_display = ['windcode', 'nav', 'nav_adj', 'date']
    search_fields = ['windcode']


@admin.register(models.BasicInfo)
class BasicInfo(admin.ModelAdmin):
    list_display = ['windcode', 'sec_name', 'setup_date', 'company', 'first_invest_type', 'update_date']
    search_fields = ['windcode', 'sec_name']


@admin.register(models.Classify)
class ClassifyAdmin(admin.ModelAdmin):
    list_display = ["windcode", "branch", "classify", "update_date"]
    search_fields = ["branch", "classify"]


@admin.register(models.Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ["windcode", "fund_fundmanager", "fund_corp_fundmanagementcompany", "update_date"]


@admin.register(models.ManagerExpand)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ["windcode", "fund_manager_resume"]


@admin.register(models.Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ["port_id", "port_name", "port_type"]
    search_fields = ['port_name']


@admin.register(models.Index)
class IndexAdmin(admin.ModelAdmin):
    list_display = ['windcode', 'launch_date', 'kind']


@admin.register(models.IndicatorIndex)
class IndicatorIndexAdmin(admin.ModelAdmin):
    list_display = ['windcode', 'indicator', 'numeric', 'text', 'note', 'rpt_date', 'update_date']


@admin.register(models.Basic)
class BasicAdmin(admin.ModelAdmin):
    list_display = ['windcode', 'sec_name', 'company', 'invest_type']


@admin.register(models.Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ['windcode', 'label']
