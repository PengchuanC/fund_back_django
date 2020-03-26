# 对应前端基金信息界面的基金表现界面，参考策略评估报告设计本页面


from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q

import pandas as pd

from api import util
from api import models


class EvaluationViews(APIView):

    def get(self, request):
        windcode = request.query_params.get('windcode')
        benchmark = request.query_params.get('benchmark', '000300.SH')
        nav = models.FundNav.objects.filter(Q(windcode=windcode)).values('date', 'nav_adj').distinct()
        bench = models.IndexClosePrice.objects.filter(Q(windcode=benchmark)).values('date', 'close').distinct()
        nav = pd.DataFrame(nav)
        bench = pd.DataFrame(bench)
        data = pd.merge(nav, bench, on='date', how="left")
        data = data.rename(columns={'nav_adj': 'fund', 'close': 'benchmark'})
        start = min(data['date']).strftime("%Y-%m-%d")
        end = max(data['date']).strftime("%Y-%m-%d")
        data = data.drop_duplicates(['date'])
        data = data.drop_duplicates(['fund', 'benchmark'])
        data = data.set_index('date')
        ret = {}
        ret.update({'duration': [start, end]})
        product = ProductInfo(windcode)
        ret.update(product.run())
        ret.update(self.format(data))
        return Response(ret)

    @staticmethod
    def format(data):
        ret = {}

        for item in [
            'acc_return_yield', 'annualized_return_yield', 'daily_change', 'trading_day_count', 'annualized_volatility',
            'max_drawback', 'sharpe_ratio', 'calmar_ratio', 'sortino_ratio'
        ]:
            n = getattr(util.Formula, item)(data).to_dict()
            ret.update({item: n})
        return ret


class ProductInfo(object):
    def __init__(self, windcode):
        self.windcode = windcode

    @property
    def product_name(self):
        ret = models.BasicInfo.objects.filter(windcode=self.windcode).values('fullname', 'company').first()
        return ret

    @property
    def product_classify(self):
        latest = util.latest(models.Classify)
        classify = models.Classify.objects.filter(
            Q(update_date=latest) & Q(windcode=self.windcode)
        ).values('classify').first()
        return classify['classify']

    @property
    def product_manager(self):
        manager = models.Manager.objects.filter(
            Q(windcode=self.windcode)
        ).values('fund_fundmanager').first()
        return manager['fund_fundmanager']

    def run(self):
        product = self.product_name
        product.update({'classify': self.product_classify})
        product.update({'manager': self.product_manager})
        return product
