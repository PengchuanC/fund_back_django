from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, Max

import pandas as pd

from api import util, models, serializer


class ProductTypeViews(APIView):
    def get(self, request):
        return Response(product_type())


class ProductFilterViews(APIView):
    def post(self, request):
        params = request.data
        print(params)
        filter_public(params['public'])
        return Response(params)


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
        codes.append(code)
    return list(set(codes))
