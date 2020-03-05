from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import Q

from api import util, models, serializer

from datetime import date, timedelta
import pandas as pd


class NavOfPrivateFundViews(APIView):
    def get(self, request):
        windcode = request.query_params.get('windcode')
        date_length = request.query_params.get('dateLength')
        benchmark = request.query_params.get('benchmark')
        data = NavOfPrivateFundViews.process(windcode, date_length, benchmark)
        return Response(data)

    @staticmethod
    def process(windcode, date_length, benchmark):
        today = date.today()
        if date_length == '6M':
            ago = today - timedelta(30 * 6)
        elif date_length == '1Y':
            ago = today - timedelta(365 * 1)
        elif date_length == '3Y':
            ago = today - timedelta(365 * 3)
        else:
            ago = today - timedelta(365 * 20)
        queryset = models.FundNav.objects.filter(
            Q(windcode=windcode) & Q(date__range=(ago, today))
        )
        data = queryset.values('date', 'nav', 'nav_adj').order_by('date')
        queryset_b = models.IndexClosePrice.objects.filter(
            Q(windcode=benchmark) & Q(date__range=(ago, today))
        ).values('date', 'close').order_by('date')
        data = pd.DataFrame(data)
        ben = pd.DataFrame(queryset_b)
        data = pd.merge(ben, data.copy(), how='outer', on='date')
        data = data[~data['nav_adj'].isnull()]
        data = data.fillna(method='ffill')
        return data.to_dict(orient='records')
