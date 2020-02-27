from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

from api import util
from api import models


class SummaryViews(APIView):
    def get(self, request):
        latest = util.latest(models.Classify)
        queryset = models.Fund.objects.filter(classify__update_date=latest).values_list(
            "windcode", "classify__branch", "classify__classify", "classify__update_date"
        )
        paginator = PageNumberPagination()
        paginator.page_query_param = "page"
        ret = paginator.paginate_queryset(queryset, request, self)
        ret = [{
            "windcode": x[0], "branch": x[1], "classify": x[2], "update_date": x[3].strftime("%Y-%m-%d")
        } for x in ret]
        return Response({"data": ret, "page": paginator.page.number, "per_page": paginator.page_size,
                         "total": queryset.count(), "date": latest.strftime("%Y-%m-%d")})


class SummaryInfoViews(APIView):
    def get(self, request):
        latest_classify = util.latest(models.Classify)
        latest_basic = util.latest(models.BasicInfo)
        queryset = models.Fund.objects.filter(
            Q(classify__update_date=latest_classify) & Q(basicinfo__update_date=latest_basic)
        ).values_list(
            "windcode", "classify__branch", "classify__classify", "basicinfo__sec_name", "basicinfo__benchmark",
            "basicinfo__setup_date"
        )
        paginator = PageNumberPagination()
        paginator.page_query_param = "page"
        ret = paginator.paginate_queryset(queryset, request, self)
        ret = [{
            "windcode": x[0], "branch": x[1], "classify": x[2], "sec_name": x[3], "benchmark": x[4], "setupdate": x[5]
        } for x in ret]
        return Response({"data": ret, "page": paginator.page.number, "per_page": paginator.page_size,
                         "total": queryset.count()})


class BranchClassifyViews(APIView):
    def get(self, request):
        # ret = util.summarise()
        ret = util.summarise2()
        return Response(ret)
