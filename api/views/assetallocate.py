from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, Max

import pandas as pd

from api import util, models, serializer


class AssetViews(APIView):
    def get(self, request):
        windcode = AssetViews.arg_parse(request)
        asset = self.asset(windcode)
        industry = self.industry(windcode)
        stock = self.stock(windcode)
        bond = self.bond(windcode)
        ret = {
            "asset": asset, "industry": industry, "stock": stock, "bond": bond
        }
        return Response(ret)

    @staticmethod
    def arg_parse(request):
        windcode = request.query_params.get('windcode')
        return windcode

    def asset(self, windcode):
        """资产配置比例"""
        rpt_date = models.Asset.objects.filter(windcode=windcode).order_by('windcode').values_list('date')
        rpt_date = [x[0] for x in rpt_date]
        if not rpt_date:
            return
        ret = models.Asset.objects.filter(Q(windcode=windcode) & Q(date__in=rpt_date[-2:])).values_list(
            'stock', 'bond', 'fund', 'warrant', 'cash', 'other', 'status'
        ).order_by('status')
        change = ret[0]
        value = ret[1]
        names = ["股票", "债券", "基金", "权证", "现金", "其他"]
        ret = [[names[x], round(value[x], 2), round(change[x], 2)] for x in range(0, len(names))]
        return ret

    def industry(self, windcode):
        """行业配置-针对股票仓位"""
        ai = models.AssetIndustry.objects
        rpt_date = ai.filter(windcode=windcode).values_list('date').order_by('industry', '-date').values_list('date')
        rpt_date = [x[0] for x in rpt_date]
        if not rpt_date:
            return
        latest = ai.filter(Q(windcode=windcode) & Q(date=rpt_date[0])).order_by('rank').all()
        if sum([x.ratio for x in latest]) == 0:
            return
        prev = ai.filter(Q(windcode=windcode) & Q(date=rpt_date[-1])).order_by('rank').all()
        change = [round(latest[i].ratio-prev[i].ratio, 2) for i in range(0, len(latest))]
        ret = [[latest[i].industry, round(latest[i].ratio, 2), change[i]] for i in range(0, len(latest)) if latest[i].ratio]
        ret = sorted(ret, key=lambda x: x[1], reverse=True)
        return ret

    def stock(self, windcode):
        """10大重仓股"""
        sh = models.StockHolding.objects
        latest = sh.filter(windcode=windcode).order_by('-date').values_list('date').first()
        if not latest:
            return
        latest = latest[0]
        latest = latest
        ret = sh.filter(Q(windcode=windcode) & Q(date=latest)).values_list('stock_name', 'ratio', 'change')
        ret = [[x[0], round(x[1], 2), round(x[2], 2)] for x in ret]
        return ret

    def bond(self, windcode):
        """10大重债券"""
        bh = models.BondHolding.objects
        latest = bh.filter(windcode=windcode).order_by('-date').values_list('date').first()
        if not latest:
            return
        latest = latest[0]
        latest = latest
        ret = bh.filter(Q(windcode=windcode) & Q(date=latest)).values_list('bond_name', 'ratio', 'change')
        ret = [[x[0], round(x[1], 2), round(x[2], 2)] for x in ret]
        return ret
