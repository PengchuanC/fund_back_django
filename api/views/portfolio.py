from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q

import pandas as pd

from datetime import date

from api import util
from api import models


class PortfolioViews(APIView):
    def get(self, request):
        ret = models.Portfolio.objects.values('port_id', 'port_name', 'port_type')
        return Response(ret)


class PortfolioInfoViews(APIView):
    @staticmethod
    def process(request):
        port_id = request.query_params.get('port_id')
        _type = request.query_params.get('port_type')
        date = request.query_params.get('date')
        portfolio = models.PortfolioExpand.objects
        latest = date
        if not date and _type != '4':
            report_dates = portfolio.filter(Q(port_id=port_id) & Q(port_type=_type)) \
                .order_by('-update_date').values_list('update_date').distinct()
            report_dates = [x[0] for x in report_dates]
            latest = report_dates[0]
        if _type in ['1', '2']:
            ret = portfolio.filter(Q(port_id=port_id) & Q(update_date=latest) & Q(port_type=_type)).values_list(
                'windcode')
            new = [x[0] for x in ret]  # 最新一期
            report_dates = portfolio.filter(Q(port_id=port_id) & Q(port_type=_type)) \
                .order_by('-update_date').values_list('update_date').distinct()
            report_dates = [x[0] for x in report_dates]
            if len(report_dates) <= 1:
                prev = []
                old = []
            else:
                prev_rpt = report_dates[1]
                ret = portfolio.filter(Q(port_id=port_id) & Q(update_date=prev_rpt) & Q(port_type=_type)).values_list(
                    'windcode')
                prev = [x[0] for x in ret]  # 上一期
                ret = portfolio.filter(Q(port_id=port_id) & Q(update_date__lt=prev_rpt) & Q(port_type=_type)).values_list(
                    'windcode')
                old = list({x[0] for x in ret})  # 历史
            add = [x for x in new if all({x not in prev, x not in old})]    # 新增
            hold = [x for x in new if x in prev]    # 保持
            back = [x for x in new if all({x not in prev, x in old})]   # 回归
            delete = [x for x in prev if x not in new]
        elif _type == '3':
            ret = portfolio.filter(Q(port_id=port_id) & Q(port_type=_type)).values_list('windcode')
            add = [x[0] for x in ret]  # 最新一期
            hold = []
            back = []
            delete = []
        else:
            ret = models.Basic.objects.filter(comment__isnull=False).values_list('windcode')
            add = [x[0] for x in ret]  # 最新一期
            hold = []
            back = []
            delete = []
        ret = {}
        for item in add:
            ret[item] = '新增'
        for item in hold:
            ret[item] = '保持'
        for item in back:
            ret[item] = '回归'
        for item in delete:
            ret[item] = '删除'
        return ret

    @staticmethod
    def retrieve_data(codes: dict):
        types = codes
        ret = list(types.keys())
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

        manager = models.Manager.objects.filter(windcode__in=codes).values('windcode', 'fund_fundmanager')
        manager = pd.DataFrame(manager).set_index('windcode')

        df = pd.merge(basic_info, indicators, left_index=True, right_index=True, how="inner")
        df = pd.merge(df, performance, left_index=True, right_index=True, how="inner")
        df = pd.merge(df, manager, left_index=True, right_index=True, how='outer')
        df = df.rename(columns={
            "sec_name": "基金简称", "setup_date": "成立日期", 'FUND_FUNDSCALE': "基金规模(亿元)",
            'NETASSET_TOTAL': "基金资产", 'NAV': "当前净值", 'NAV_ACC': "累计净值",
            'RETURN_1M': "近1月回报", 'RETURN_1Y': "近1年回报",
            'RETURN_3M': "近3月回报", 'RETURN_3Y': "近3年回报",
            'RETURN_6M': "近6月回报", 'RETURN_STD': "成立年化回报",
            'RETURN_1W': "近1周回报", 'fund_fundmanager': '基金经理'
        })
        df['成立日期'] = df['成立日期'].apply(lambda x: x.strftime("%Y/%m/%d"))
        df["基金代码"] = df.index
        for col in ["基金规模(亿元)", "基金资产", "当前净值", "累计净值", "近1月回报", "近3月回报", "近6月回报", "近1年回报", "近3年回报", "成立年化回报", "近1周回报"]:
            df[col] = df[col].apply(lambda x: round(x, 2))
        df = df.fillna(0)
        ret = df.to_dict(orient="record")
        return ret

    @staticmethod
    def normal_pool(request):
        """观察池、核心池"""
        data = PortfolioInfoViews.process(request)
        ret = PortfolioInfoViews.retrieve_data(data)
        for x in ret:
            x['状态'] = data.get(x['基金代码'])
        return ret

    @staticmethod
    def invest_pool(request):
        """备投池"""
        portfolio = models.PortfolioExpand.objects
        ret = portfolio.filter(port_type='3').values('windcode', 'port_id__port_name')
        data = {}
        for x in ret:
            data[x['windcode']] = x['port_id__port_name']
        ret = PortfolioInfoViews.retrieve_data(data)
        for x in ret:
            x['状态'] = data.get(x['基金代码'])
        return ret

    @staticmethod
    def visit_pool(request):
        """访谈池"""
        ret = models.Basic.objects.filter(comment__isnull=False).values_list('windcode')
        data = {}
        for x in ret:
            data[x[0]] = '新增'
        ret = PortfolioInfoViews.retrieve_data(data)
        for x in ret:
            x['状态'] = data.get(x['基金代码'])
        return ret

    def get(self, request):
        port_type = request.query_params.get('port_type')
        if port_type in ['1', '2']:
            data = PortfolioInfoViews.normal_pool(request)
        elif port_type == '3':
            data = PortfolioInfoViews.invest_pool(request)
        else:
            data = PortfolioInfoViews.visit_pool(request)
        return Response(data)

    def put(self, request):
        params = request.data
        windcode = params.get('windcode')
        port_id = params.get('port_id')
        if windcode:
            try:
                for w in windcode:
                    p = models.Portfolio.objects.get(port_id=port_id)
                    pe = models.PortfolioExpand(windcode=w, port_id=p, port_type=3, update_date=date.today())
                    pe.save()
                return Response({'msg': 'success'})
            except Exception as e:
                print(e)
                return Response({'msg': 'failed', 'error': str(e)})

    def delete(self, request):
        params = request.data
        windcode = params.get('windcode')
        port_id = params.get('port_id')
        if windcode:
            try:
                for w in windcode:
                    pe = models.PortfolioExpand.objects.filter(Q(windcode=w) & Q(port_id__port_id=port_id))
                    pe.delete()
                return Response({'msg': 'success'})
            except Exception as e:
                print(e)
                return Response({'msg': 'failed', 'error': str(e)})


class PortfolioDateViews(APIView):
    def get(self, request):
        port_id = request.query_params.get('port_id')
        _type = request.query_params.get('port_type')
        portfolio = models.PortfolioExpand.objects
        dates = portfolio.filter(Q(port_id=port_id) & Q(port_type=_type)).values_list('update_date').distinct()
        dates = [x[0] for x in dates]
        return Response(dates)


class CommentViews(APIView):
    def get(self, request):
        windcode = request.query_params.get('windcode')
        if windcode:
            query = models.Basic.objects.filter(windcode=windcode).values('windcode', 'sec_name', 'comment')[0]
        else:
            query = models.Basic.objects.filter(comment__isnull=False).values('windcode', 'sec_name', 'comment')
        return Response(query)

    def put(self, request):
        windcode = request.data.get('windcode')
        comment = request.data.get('comment', '')
        fund = models.Basic.objects.get(windcode=windcode)
        if len(comment) == 0:
            fund.comment = None
        else:
            fund.comment = comment
        fund.save()
        return Response()
