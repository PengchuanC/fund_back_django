from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, Max

import pandas as pd

from datetime import date

from api import util
from api import models


class PortfolioViews(APIView):
    def get(self, request):
        ret = models.Portfolio.objects.values('port_id', 'port_name', 'port_type')
        ret = [{'port_id': 0, 'port_name': '全部组合', 'port_type': 1}] + [x for x in ret]
        return Response(ret)


class PortfolioInfoViews(APIView):
    @staticmethod
    def process(request):
        port_id = request.query_params.get('port_id')
        _type = request.query_params.get('port_type')
        date = request.query_params.get('date')
        portfolio = models.PortfolioExpand.objects
        latest = date
        if port_id[0] == '0':
            if _type != "4":
                latest = portfolio.filter(port_type=1).aggregate(Max('update_date'))['update_date__max']
                if _type in ['1', '2']:
                    ret = portfolio.filter(Q(port_type=_type)
                                           & Q(update_date=latest)).values_list("windcode").distinct()
                else:
                    ret = portfolio.filter(port_type=_type).values_list('windcode').distinct()
            else:
                ret = models.Basic.objects.filter(comment__isnull=False).values_list('windcode')
            ret = {x[0]: "-" for x in ret}
            return ret
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
    def retrieve_data(codes: list):
        funds = list(codes.keys())
        latest_ind = util.latest(models.Indicator)
        latest_performance = util.latest(models.FundPerformance)
        ret = models.Fund.objects.filter(
            Q(windcode__in=funds) & Q(indicator__update_date=latest_ind) & Q(indicator__indicator='FUND_FUNDSCALE')
        ).values(
            'windcode', 'basicinfo__sec_name', 'basicinfo__setup_date', 'indicator__numeric',
            'manager__fund_fundmanager'
        ).distinct()
        data = pd.DataFrame(ret).set_index('windcode')
        performance = models.FundPerformance.objects.filter(
            Q(windcode_id__in=funds) & Q(update_date=latest_performance)
        ).values('windcode', 'indicator', 'value').distinct()

        performance = pd.DataFrame(performance).pivot("windcode", "indicator")["value"]
        data = pd.merge(data, performance, left_index=True, right_index=True, how='outer')
        df = data.rename(columns={
            "basicinfo__sec_name": "基金简称", "basicinfo__setup_date": "成立日期", 'indicator__numeric': "基金规模(亿元)",
            'NAV': "当前净值", 'NAV_ACC': "累计净值",
            'RETURN_1M': "近1月回报", 'RETURN_1Y': "近1年回报",
            'RETURN_3M': "近3月回报", 'RETURN_3Y': "近3年回报",
            'RETURN_6M': "近6月回报", 'RETURN_STD': "成立年化回报",
            'RETURN_1W': "近1周回报", 'manager__fund_fundmanager': '基金经理'
        })
        df["基金规模(亿元)"] = round(df["基金规模(亿元)"]/1e8, 2)
        df['成立日期'] = df['成立日期'].apply(lambda x: x.strftime("%Y/%m/%d"))
        df["基金代码"] = df.index
        for col in ["基金规模(亿元)", "当前净值", "近1月回报", "近3月回报", "近6月回报", "近1年回报", "近3年回报", "成立年化回报", "近1周回报"]:
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
        port_id = request.query_params.get('port_id')
        portfolio = models.PortfolioExpand.objects
        if port_id == "0":
            ret = portfolio.filter(Q(port_type='3')).values('windcode', 'port_id__port_name')
        else:
            ret = portfolio.filter(Q(port_type='3') & Q(port_id=port_id)).values('windcode', 'port_id__port_name')
        latest = util.latest(models.Classify)
        funds = {x['windcode'] for x in ret}
        data = models.Classify.objects.filter(
            Q(windcode__in=funds) & Q(update_date=latest)).values_list("windcode", "classify").distinct()
        data = {x[0]: x[1] for x in data}
        ret = PortfolioInfoViews.retrieve_data(data)
        for x in ret:
            x['状态'] = data.get(x['基金代码'])
        return ret

    @staticmethod
    def visit_pool(request):
        """访谈池"""
        port_id = request.query_params.get('port_id')
        if port_id == "0":
            ret = models.Basic.objects.filter(comment__isnull=False).values_list('windcode')
        else:
            port_name = models.Portfolio.objects.filter(port_id=port_id).values('port_name').first()['port_name']
            latest = util.latest(models.Classify)
            ret = models.Basic.objects.filter(
                Q(comment__isnull=False) & Q(windcode__classify__classify=port_name)
                & Q(windcode__classify__update_date=latest)
            ).values_list('windcode').distinct()
        latest = util.latest(models.Classify)
        funds = {x[0] for x in ret}
        data = models.Classify.objects.filter(
            Q(windcode__in=funds) & Q(update_date=latest)).values_list("windcode", "classify").distinct()
        data = {x[0]: x[1] for x in data}
        ret = PortfolioInfoViews.retrieve_data(data)
        for x in ret:
            x['状态'] = data.get(x['基金代码'])
        return ret

    @staticmethod
    def classify_by_windcode(windcode):
        latest = util.latest(models.Classify)
        cls = models.Classify.objects.filter(Q(windcode=windcode) & Q(update_date=latest)).values("classify").first()
        return cls['classify']

    @staticmethod
    def portid_by_portname(port_name):
        port_id = models.Portfolio.objects.filter(Q(port_name=port_name)).values("port_id").first()
        if port_id is None:
            return 10
        return port_id['port_id']

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
                    cls = self.classify_by_windcode(w)
                    _port_id = self.portid_by_portname(cls)
                    print(_port_id)
                    p = models.Portfolio.objects.get(port_id=_port_id)
                    pe = models.PortfolioExpand(windcode=w, port_id=p, port_type=3, update_date=date.today())
                    pe.save()
                return Response({'msg': 'success', 'info': f"添加{w}到{cls}"})
            except Exception as e:
                print(e)
                return Response({'msg': 'failed', 'info': f"没有组合-{cls}"})

    def delete(self, request):
        params = request.data
        windcode = params.get('windcode')
        if windcode:
            try:
                for w in windcode:
                    cls = self.classify_by_windcode(w)
                    _port_id = self.portid_by_portname(cls)
                    pe = models.PortfolioExpand.objects.filter(Q(windcode=w) & Q(port_id__port_id=_port_id))
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
        if comment is not None and len(comment) == 0:
            fund.comment = None
        fund.comment = comment
        fund.save()
        return Response()
