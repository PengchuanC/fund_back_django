from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q

from pandas import cut
from math import ceil

from api import util
from api import models


class BranchView(APIView):
    def get(self, request):
        latest = util.latest(models.Classify)
        classify = models.Classify.objects.filter(update_date=latest).all().values('branch', 'classify').distinct()
        branch = list(set([x['branch'] for x in classify]))
        bc = {x: [] for x in branch}
        for c in classify:
            bc[c['branch']].append(c['classify'])
        ret = {"data": bc, "branch": branch}
        return Response(ret)


class ExistViews(APIView):
    def get(self, request):
        classify = parse_classify(request)
        ret = ExistViews.process(classify)
        return Response(ret)

    @staticmethod
    def process(classify):
        IFP = models.IndicatorForPlot
        latest = util.latest(IFP)
        funds = query_funds_by_classify(classify)
        data = IFP.objects.filter(Q(update_date=latest) & Q(windcode_id__in=funds)).all().values('fund_setupdate')
        data = [x['fund_setupdate'] for x in data]
        years = [(latest - x).days / 365 for x in data]
        mean = sum(years) / len(years) if len(years) else 0
        _max = max(years)
        years = cut(years, bins=range(0, ceil(_max)), labels=range(0, ceil(_max) - 1))
        years = (years.value_counts() / len(years)).to_dict()
        years = [{"存续年限": x, "频率分布": y} for x, y in years.items() if y != 0]
        years = sorted(years, key=lambda x: x['存续年限'])
        ret = {"data": years, "mean": mean, "classify": classify, "date": latest.strftime("%Y-%m-%d")}
        return ret


class ScaleViews(APIView):
    def get(self, request):
        classify = parse_classify(request)
        ret = ScaleViews.process(classify)
        return Response(ret)

    @staticmethod
    def process(classify):
        IFP = models.IndicatorForPlot
        latest = util.latest(IFP)
        funds = query_funds_by_classify(classify)
        data = IFP.objects.filter(Q(update_date=latest) & Q(windcode_id__in=funds)).all().values('prt_netasset')
        data = [x['prt_netasset'] / (10 ** 8) for x in data if x['prt_netasset']]
        _max = max(data)
        count = len(data)
        # 将x轴20等分
        data = cut(data, bins=range(0, ceil(_max / 20) * 20 - ceil(_max / 20), ceil(_max / 20)))
        data = (data.value_counts() / count).to_dict()
        data = [{"规模分布": (int(x.left), int(x.right)), "频率分布": y} for x, y in data.items() if y]
        ret = {"data": data, "classify": classify, "date": latest.strftime("%Y-%m-%d")}
        return ret


class CompanyViews(APIView):
    def get(self, request):
        classify = parse_classify(request)
        ret = CompanyViews.process(classify)
        return Response(ret)

    @staticmethod
    def process(classify):
        IFP = models.IndicatorForPlot
        latest = util.latest(IFP)
        funds = query_funds_by_classify(classify)
        data = IFP.objects.filter(Q(update_date=latest) & Q(windcode_id__in=funds)).all().values('prt_netasset', 'fund_corp_fundmanagementcompany')
        data = [x for x in data if x['prt_netasset']]
        company = list(set([x['fund_corp_fundmanagementcompany'] for x in data]))
        company = {x: 0 for x in company}
        for x in data:
            company[x['fund_corp_fundmanagementcompany']] += x['prt_netasset'] / (10 ** 8)
        company = [{"基金公司": x, "基金资产": y} for x, y in company.items()]
        company = sorted(company, key=lambda x: x['基金资产'], reverse=True)
        cumsum = sum(x['基金资产'] for x in company)
        cum = 0
        for i in range(0, len(company)):
            cum += company[i]['基金资产']
            company[i]['占比'] = cum / cumsum
        ret = {"data": company, "classify": classify, "date": latest.strftime("%Y-%m-%d")}
        return ret


class ScaleYearViews(APIView):
    def get(self, request):
        classify = parse_classify(request)
        ret = ScaleYearViews.process(classify)
        return Response(ret)

    @staticmethod
    def process(classify):
        IFP = models.IndicatorForPlot
        latest = util.latest(IFP)
        funds = query_funds_by_classify(classify)
        data = models.Fund.objects.filter(
            Q(windcode__in=funds) & Q(indicatorforplot__update_date=latest)
        ).all().values('basicinfo__sec_name', 'indicatorforplot__prt_netasset', 'indicatorforplot__fund_setupdate')
        data = [
            {"基金简称": x['basicinfo__sec_name'], "基金规模": round(x['indicatorforplot__prt_netasset'] / (10 ** 8), 2),
             "存续时间": round((latest - x['indicatorforplot__fund_setupdate']).days / 365, 2)}
            for x in data if x["basicinfo__sec_name"] if all({x['indicatorforplot__prt_netasset'], x['indicatorforplot__fund_setupdate']})
        ]
        data = sorted(data, key=lambda x: x["存续时间"])
        data = [{"基金简称": x["基金简称"], "存续时间": x["存续时间"], "基金规模": x["基金规模"], "近似年限": int(x["存续时间"])} for x in data]
        ret = {"data": data, "classify": classify, "date": latest.strftime("%Y-%m-%d")}
        return ret


class PlotManagerViews(APIView):
    def post(self, request):
        classify = request.data.get("classify")
        latest = util.latest(models.Classify)
        funds = models.Classify.objects.filter(Q(classify__in=classify)&Q(update_date=latest)).all().values('windcode')
        funds = list({x['windcode'] for x in funds})
        latest = util.latest(models.Indicator)
        ret = models.Fund.objects.filter(
            Q(windcode__in=funds) & Q(indicator__indicator="FUND_MANAGER_MANAGERWORKINGYEARS")
            & Q(indicator__update_date=latest), Q(manager__manager_info__rank=1)
        ).all().values(
            'manager__fund_fundmanager', 'manager__manager_info__fund_manager_totalnetasset',
            'manager__manager_info__nav_periodicannualizedreturn', 'indicator__numeric'
            )
        ret = [[round(x["indicator__numeric"], 2) if x["indicator__numeric"] else 0,
                round(x['manager__manager_info__nav_periodicannualizedreturn'], 4),
                round(x['manager__manager_info__fund_manager_totalnetasset']/1e8, 2),
                x['manager__fund_fundmanager']] for x in ret]
        return Response(ret)


class PlotViews(APIView):
    def get(self, request):
        classify = parse_classify(request)
        exist_data = ExistViews.process(classify)
        scale_data = ScaleViews.process(classify)
        comp = CompanyViews.process(classify)
        sc_y = ScaleYearViews.process(classify)
        return Response({"data": {
            "exist": exist_data["data"], "scale": scale_data["data"], 'company': comp["data"], "scale_year": sc_y["data"]
        }, "classify": classify, "date": exist_data['date']})


def parse_classify(request):
    classify = request.query_params.get('classify')
    return classify


def query_funds_by_classify(classify):
    latest = util.latest(models.Classify)
    funds = models.Classify.objects.filter(Q(classify=classify) & Q(update_date=latest)).all().values('windcode')
    funds = list({x['windcode'] for x in funds})
    return funds
