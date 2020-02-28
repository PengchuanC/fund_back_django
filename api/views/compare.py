from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, Max

import math
import pandas as pd
import numpy as np
from datetime import date

from api import util, models, serializer


class ProductTypeViews(APIView):
    def get(self, request):
        return Response(product_type())


class ProductFilterViews(APIView):
    def post(self, request):
        params = request.data
        print(params)
        public = filter_public(params.get('public'))
        private = filter_private(params.get('private'), params.get('privateLabel'))
        private = performance_private(private)
        return Response(private)


def product_type():
    """获取产品类型"""
    latest_public = util.latest(models.Classify)
    public = models.Classify.objects.filter(update_date=latest_public).values("branch", "classify").distinct()
    # public = [x[0] for x in public]
    private_label = models.Label.objects.values_list("label").distinct()
    private_label = list({x[0] for x in private_label})
    private = models.Fund.objects.filter(category=2).values_list("basic__invest_type").distinct()
    private = [x[0] for x in private if x]
    wealth = models.Fund.objects.filter(category=3).values_list("basic__invest_type").distinct()
    wealth = [x[0] for x in wealth if x]
    return {"public": public, "privateLabel": private_label, "private": private, "wealth": wealth}


def filter_public(public):
    codes = []
    latest = util.latest(models.Classify)
    for f in public:
        code = models.Classify.objects.filter(
            Q(branch=f['branch']) & Q(classify=f['classify']) & Q(update_date=latest)
        ).values_list('windcode').distinct()
        code = [x[0] for x in code]
        codes.extend(code)
    return list(set(codes))


def filter_private(private, private_label):
    print(private, private_label)
    if not private and not private_label:
        queryset = models.Basic.objects.filter(windcode__category=2).values_list("windcode")
        codes = list({x[0] for x in queryset})
    elif not private and private_label:
        queryset = models.Label.objects.filter(
            label__in=private_label
        ).values_list("windcode")
        codes = list({x[0] for x in queryset})
    elif private and not private_label:
        queryset = models.Basic.objects.filter(
            invest_type__in=private
        ).values_list("windcode")
        codes = list({x[0] for x in queryset})
    else:
        queryset = models.Basic.objects.filter(
            Q(invest_type__in=private) & Q(invest_type__in=private)
        ).values_list("windcode")
        codes = list({x[0] for x in queryset})
    return codes


def performance(codes):
    """此处待修改"""
    print(codes)
    day = f"{date.today().year-1}-01-01"
    data = models.FundNav.objects.filter(
        Q(windcode__in=codes) & Q(date__gt=day)
    ).values("windcode_id", "date", "nav_adj")
    data = pd.DataFrame(data).sort_values('date')
    data = pd.pivot_table(data, index='date', columns='windcode_id', values='nav_adj')
    data = data.fillna(method="bfill")
    data = data.fillna(method="ffill")
    pct = np.round(data.iloc[-1, :] / data.iloc[0, :] - 1, 4)
    pct.name = "ytd"
    std = np.round(data.std()*math.sqrt(52), 4)
    std.name = "sigma"
    data = pd.DataFrame([pct, std]).T
    data['windcode_id'] = data.index
    data = data.reset_index(drop=True)
    # data = data.to_dict(orient="records")
    return data


def performance_private(codes):
    perf = performance(codes)
    info = models.Basic.objects.filter(windcode__in=codes).values(
        "windcode_id", "sec_name", "company", "invest_type"
    )
    info = pd.DataFrame(info)
    data = pd.merge(info, perf, how="inner", on="windcode_id")
    tile_025 = data.quantile(0.25)
    mean = data.mean()
    mean.name = "mean"
    tile_050 = data.quantile(0.5)
    tile_075 = data.quantile(0.75)
    tile = pd.DataFrame([tile_025, mean, tile_050, tile_075])
    tile = tile.to_dict()
    data = data.to_dict(orient="records")
    return {"data": data, "percent": tile}
