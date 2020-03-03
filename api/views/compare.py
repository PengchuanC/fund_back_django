from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, Max

import pandas as pd

from api import util, models, serializer
from api.util.performance import Performance


class ProductTypeViews(APIView):
    def get(self, request):
        return Response(product_type())


class ProductFilterViews(APIView):
    def post(self, request):
        params = request.data
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
    data = models.FundNav.objects.filter(windcode__in=codes).values("windcode_id", "revised_date", "nav_adj").distinct()
    data = pd.DataFrame(data).sort_values('revised_date')
    data = pd.pivot_table(data, index='revised_date', columns='windcode_id', values='nav_adj')
    ret = []
    for code in data.columns:
        p = Performance(data[code])
        ret.append({'windcode_id': code, 'r1y': p.r1y(), 'r3y': p.r3y(), 'ytd': p.ytd(), 'sigma': p.sigma()})
    ret = pd.DataFrame(ret)
    ret = ret[ret['r1y'].notnull()]
    return ret


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
