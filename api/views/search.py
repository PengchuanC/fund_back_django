from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q

from api import models


class SearchViews(APIView):
    def get(self, request):
        queryset = models.BasicInfo.objects.all().values("windcode", "sec_name").distinct()[:10]
        ret = [(x['windcode'], x['sec_name']) for x in queryset]
        return Response(ret)

    def post(self, request):
        search = request.data.get("search")
        queryset = models.Basic.objects.filter(
            Q(windcode__windcode__contains=search) | Q(sec_name__contains=search)
        ).values('windcode', 'sec_name').distinct()
        ret = [(x['windcode'], x['sec_name']) for x in queryset]
        return Response(ret[:10])
