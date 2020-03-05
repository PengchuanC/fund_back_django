from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from news.models import News


class NewsResource(resources.ModelResource):
    class Meta:
        model = News


@admin.register(News)
class NewsAdmin(ImportExportModelAdmin):
    list_display = ('title', 'source', 'keyword', 'url')
    search_fields = ('title', 'keyword')
    resource_class = NewsResource
