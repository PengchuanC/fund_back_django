from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q

import pandas as pd

from api import util
from api import models


class PortfolioViews(APIView):
    def get(self, request):
        ret = models.Portfolio.objects.values('port_id', 'port_name', 'port_type')
        return Response(ret)


class PortfolioInfoViews(APIView):
    def get(self, request):
        port_id = request.query_params.get('port_id')
        _type = request.query_params.get('port_type')
        date = request.query_params.get('date')
        latest = date
        if not latest:
            latest = util.latest(models.PortfolioCore)

        if _type == "核心池":
            portfolio = models.PortfolioCore.objects

        else:
            portfolio = models.PortfolioObserve.objects
        ret = portfolio.filter(Q(port_id=port_id) & Q(update_date=latest)).values_list('windcode')
        ret = [x[0] for x in ret]
        basic_info = models.BasicInfo.objects.filter(
            Q(windcode_id__in=ret)).values('windcode', 'sec_name', 'setup_date').distinct()
        basic_info = pd.DataFrame(basic_info).set_index("windcode")

        latest_ind = util.latest(models.Indicator)
        indicators = models.Indicator.objects.filter(
            Q(indicator__in=["NETASSET_TOTAL", "FUND_FUNDSCALE"]) | Q(update_date=latest_ind) & Q(windcode_id__in=ret)
        ).values('windcode', 'numeric', 'indicator').distinct()
        indicators = pd.DataFrame(indicators)
        indicators["numeric"] = indicators["numeric"].astype("float")
        indicators = indicators.drop_duplicates(['windcode', 'indicator'])
        indicators = indicators.pivot("windcode", "indicator")["numeric"]
        indicators = indicators / 1e8

        latest_performance = util.latest(models.FundPerformance)
        performance = models.FundPerformance.objects.filter(
            Q(windcode_id__in=ret) & Q(update_date=latest_performance)
        ).values('windcode', 'indicator', 'value').distinct()

        performance = pd.DataFrame(performance).pivot("windcode", "indicator")["value"]

        df = pd.merge(basic_info, indicators, left_index=True, right_index=True, how="inner")
        df = pd.merge(df, performance, left_index=True, right_index=True, how="inner")
        df = df.rename(columns={
            "sec_name": "基金简称", "setup_date": "成立日期", 'FUND_FUNDSCALE': "基金规模(亿元)",
            'NETASSET_TOTAL': "基金资产", 'NAV': "当前净值", 'NAV_ACC': "累计净值",
            'RETURN_1M': "近1月回报", 'RETURN_1Y': "近1年回报",
            'RETURN_3M': "近3月回报", 'RETURN_3Y': "近3年回报",
            'RETURN_6M': "近6月回报", 'RETURN_STD': "成立年化回报",
            'RETURN_1W': "近1周回报"
        })
        df['成立日期'] = df['成立日期'].apply(lambda x: x.strftime("%Y/%m/%d"))
        df["基金代码"] = df.index
        for col in ["基金规模(亿元)", "基金资产", "当前净值", "累计净值", "近1月回报", "近3月回报", "近6月回报", "近1年回报", "近3年回报", "成立年化回报", "近1周回报"]:
            df[col] = df[col].apply(lambda x: round(x, 2))
        df = df.fillna(0)
        ret = df.to_dict(orient="record")
        return Response(ret)


class PortfolioDateViews(APIView):
    def get(self, request):
        port_id = request.query_params.get('port_id')
        _type = request.query_params.get('port_type')
        if _type == "核心池":
            portfolio = models.PortfolioCore.objects

        else:
            portfolio = models.PortfolioObserve.objects
        dates = portfolio.filter(port_id=port_id).values_list('update_date').distinct()
        dates = [x[0] for x in dates]
        return Response(dates)
