from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, Max

from api import util, models


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
            'stock', 'bond', 'fund', 'warrant', 'cash', 'other'
        )
        change = [ret[1][x] - ret[0][x] for x in range(0, len(ret[0]))]
        value = ret[1]
        names = ["股票", "债券", "基金", "权证", "现金", "其他"]
        ret = [[names[x], round(value[x]*100, 2), round(change[x]*100, 2)] for x in range(0, len(names))]
        return ret

    def industry(self, windcode):
        """行业配置-针对股票仓位"""
        ai = models.AssetIndustry.objects
        latest = util.latest(models.AssetIndustry)
        if not latest:
            return
        ret = ai.filter(Q(windcode=windcode) & Q(update_date=latest)).values_list('industry', 'ratio', 'change')
        if sum([x[1] for x in ret]) <= 0:
            return
        ret = list(filter(lambda x: x[1] != 0, ret))
        ret = [[x[0], round(x[1], 2), round(x[2], 2) if x[2] else None] for x in ret]
        ret = sorted(ret, key=lambda x: x[1], reverse=True)
        return ret

    def stock(self, windcode):
        """10大重仓股"""
        sh = models.StockHolding.objects
        latest = sh.filter(windcode=windcode).order_by('-date').values_list('date').first()
        if not latest:
            return
        latest = latest[0]
        ret = sh.filter(Q(windcode=windcode) & Q(date=latest)).values_list('stock_name', 'ratio', 'change')
        ret = [[x[0], round(x[1]*100, 2), round(x[2]*100, 2) if x[2] else None] for x in ret]
        return ret

    def bond(self, windcode):
        """10大重债券"""
        bh = models.BondHolding.objects
        latest = bh.filter(windcode=windcode).order_by('-date').values_list('date').first()
        if not latest:
            return
        latest = latest[0]
        ret = bh.filter(Q(windcode=windcode) & Q(update_date=latest)).values_list(
            'bond_name', 'ratio', 'change'
        ).order_by('ratio')
        ret = [[x[0], round(x[1]*100, 2), round(x[2]*100, 2) if x[2] else None] for x in ret]
        return ret
