from datetime import timedelta
from functools import lru_cache
from math import floor, pow

import pandas as pd

from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

from api import models, util


@lru_cache(20)
def latest_day_in_basic_info():
    latest = util.latest(models.BasicInfo)
    return latest


@lru_cache(20)
def latest_day_in_indicators():
    latest = util.latest(models.Indicator)
    return latest


@lru_cache(20)
def latest_day_in_classify():
    latest = util.latest(models.Classify)
    return latest


def funds_by_classify_from_fund(fund):
    """根据基金代码获取同类型基金"""
    latest = util.latest(models.Classify)
    classify = models.Classify.objects.filter(
        Q(windcode=fund) & Q(update_date=latest)).values("classify", 'branch').distinct()[0]
    funds = models.Classify.objects.filter(
        Q(branch=classify['branch']) & Q(classify=classify['classify']) & Q(update_date=latest)
    ).values_list('windcode')
    funds = list({x[0] for x in funds})
    return funds


def funds_by_classify(cls: list):
    """获取特定分类下的全部基金"""
    latest = latest_day_in_classify()
    funds = models.Classify.objects.filter(Q(classify__in=cls) & Q(update_date=latest)).values_list('windcode')
    funds = {x[0] for x in funds}
    return funds


def lever(funds, yes_or_no):
    """是否是杠杆基金"""
    yes_or_no = 0 if yes_or_no == "是" else 1
    funds = models.BasicInfo.objects.filter(windcode__in=funds).values_list('windcode', 'structured')
    funds = {x[0] for x in funds if x[1] == yes_or_no}
    return funds


def fund_years(funds, left, right=50):
    """基金存续时间位于[left, right]"""
    bi = models.BasicInfo
    latest = latest_day_in_basic_info()
    left = latest - timedelta(left * 365)
    right = latest - timedelta(right * 365)
    funds = bi.objects.filter(Q(setup_date__range=(right, left)) & Q(windcode__in=funds)).values_list('windcode')
    funds = set([x[0] for x in funds])
    return funds


def regular_open(funds, yes_or_not):
    """债券型基金是否定开，关键字为是或者否"""
    ind = models.Indicator
    latest = latest_day_in_indicators()
    funds = ind.objects.filter(
        Q(update_date=latest) & Q(indicator="FUND_REGULOPENFUNDORNOT") & Q(windcode__in=funds)
    ).values_list('windcode', 'text')
    funds = list({x[0] for x in funds if x[1] == yes_or_not})
    return funds


def net_asset(funds, recent_asset_level, avg_asset_level):
    """对最新一期季报和年报的基金净值规模作出要求"""
    ins = models.Indicator
    rpt = ins.objects.values_list('rpt_date').distinct().order_by('-rpt_date')
    rpt = [x[0] for x in rpt]
    recent = rpt[0]
    annual = [x for x in rpt if x.month == 12][0]
    funds = ins.objects.filter(
        Q(windcode__in=funds) & Q(rpt_date=recent) & Q(indicator="NETASSET_TOTAL")
        & (Q(numeric__gte=recent_asset_level * 1e8) | Q(numeric__isnull=True))).values_list('windcode')
    funds = {x[0] for x in funds}
    funds = ins.objects.filter(
        Q(windcode__in=funds) & Q(rpt_date=annual) & Q(indicator="PRT_AVGNETASSET") & (Q(
            numeric__gte=avg_asset_level * 1e8) | Q(numeric__isnull=True)
    )).values_list('windcode')
    funds = {x[0] for x in funds}
    return funds


def single_hold_shares(funds, percent: int = 40):
    """单一投资者持仓比例限制，默认低于40%"""
    ins = models.Indicator
    latest = latest_day_in_indicators()
    funds = ins.objects.filter(
        Q(update_date=latest) & Q(windcode__in=funds) & Q(indicator="HOLDER_SINGLE_TOTALHOLDINGPCT")
    ).values_list('windcode', 'numeric')
    funds = [(x[0], x[1] or 0) for x in funds]
    funds = [x[0] for x in funds if x[1] <= percent]
    return funds


def organization_hold_shares(funds, percent: int = 50):
    """机构投资者持仓比例限制，默认低于50%"""
    ins = models.Indicator
    latest = latest_day_in_indicators()
    funds = ins.objects.filter(
        Q(update_date=latest) & Q(windcode__in=funds) & Q(indicator="HOLDER_INSTITUTION_HOLDINGPCT")
    ).values_list('windcode', 'numeric')
    funds = [(x[0], x[1] or 0) for x in funds]
    funds = [x[0] for x in funds if x[1] <= percent]
    return funds


def over_index_return(funds, index_code, year):
    """区间收益超过指定的指数的区间收益"""
    index_code = index_code.split(",")
    ins = models.Indicator
    latest = latest_day_in_indicators()
    funds = ins.objects.filter(
        Q(update_date=latest) & Q(indicator="RETURN") & Q(windcode__in=funds)
    ).values_list('windcode', 'numeric')
    funds = [(x[0], x[1] or 0) for x in funds]
    index = models.IndicatorIndex.objects.filter(
        Q(update_date=latest) & Q(indicator="RETURN") & Q(windcode__in=index_code) & Q(note=str(year))
    ).values_list('windcode', 'numeric')
    index = [(x[0], x[1] or 0) for x in index]
    if len(index_code) == 1:
        index = index[0]
        funds = {x[0] for x in funds if x[1] > index[1]}
    elif len(index_code) == 2:
        index = (index[0][1] + index[1][1]) / 2
        funds = {x[0] for x in funds if x[1] > index}
    return funds


def over_bench_return(funds, year):
    """区间收益超过基准
    此处应当注意如易方达中小盘等采用天相指数的基金，wind并没有相关数据，此处跳过这些检查，让基准收益 >= 0
    """
    ins = models.Indicator
    latest = latest_day_in_indicators()
    funds = ins.objects.filter(
        Q(update_date=latest) & Q(indicator="NAV_OVER_BENCH_RETURN_PER") & Q(note=str(year)) & Q(windcode__in=funds)
    ).values_list('windcode', 'numeric')
    funds = {x[0] for x in funds if x[1] >= 0}
    return funds


def month_win_ratio(funds, year, ratio=0.5):
    """月度胜率"""
    ins = models.Indicator
    latest = latest_day_in_indicators()
    funds = ins.objects.filter(
        Q(update_date=latest) & Q(indicator="ABSOLUTE_UPDOWNMONTHRATIO") & Q(note=str(year)) & Q(windcode__in=funds)
    ).values_list('windcode', 'text')
    funds = [(x[0], x[1] or "0/0") for x in funds]
    _funds = []
    for fund in funds:
        up, down = fund[1].split("/")
        if int(down) == 0:
            _funds.append(fund[0])
        else:
            if int(up) / int(down) > ratio:
                _funds.append(fund[0])

    return _funds


def max_downside_over_average(funds, year, ratio=None):
    """最大回撤优于平均"""
    ins = models.Indicator
    latest = latest_day_in_indicators()
    funds = list(funds)
    all_funds = funds_by_classify_from_fund(funds[0])
    all_funds = ins.objects.filter(
        Q(update_date=latest) & Q(indicator="RISK_MAXDOWNSIDE") & Q(note=str(year)) & Q(windcode__in=all_funds)
    ).values_list('windcode', 'numeric')
    all_funds = [(x[0], x[1] or 0) for x in all_funds]
    funds = ins.objects.filter(
        Q(update_date=latest) & Q(indicator="RISK_MAXDOWNSIDE") & Q(note=str(year)) & Q(windcode__in=funds)
    ).values_list('windcode', 'numeric')
    funds = [(x[0], x[1] or 0) for x in funds]
    if str(ratio) == "平均":
        mmd = [x[1] for x in all_funds]
        mean = sum(mmd) / len(mmd)
        funds = {x[0] for x in funds if x[1] > mean}
    else:
        funds = {x[0] for x in funds if x[1] / 100 > -ratio}
    return funds


def stdev_yearly_over_range(funds, year, ratio=None):
    """年化波动率优于平均"""
    ins = models.Indicator
    latest = latest_day_in_indicators()
    funds = list(funds)
    all_funds = funds_by_classify_from_fund(funds[0])
    all_funds = ins.objects.filter(
        Q(update_date=latest) & Q(indicator="RISK_STDEVYEARLY") & Q(windcode__in=all_funds)
    ).values_list('windcode', 'numeric')
    all_funds = [(x[0], x[1] or 0) for x in all_funds]
    funds = ins.objects.filter(
        Q(update_date=latest) & Q(indicator="RISK_STDEVYEARLY") & Q(windcode__in=funds)
    ).values_list('windcode', 'numeric')
    funds = [(x[0], x[1] or 0) for x in funds]
    if str(ratio) == "平均":
        mmd = [x[1] for x in all_funds]
        mean = sum(mmd) / len(mmd)
        funds = {x[0] for x in funds if x[1] < mean}
    else:
        funds = {x[0] for x in funds if x[1] < ratio}
    return funds


def corp_scale_level(funds, level):
    """基金公司规模大于？分位"""
    ins = models.Indicator
    latest_c = latest_day_in_classify()
    latest_i = latest_day_in_indicators()
    all_funds1 = models.Fund.objects.filter(
        Q(indicator__update_date=latest_i) & Q(classify__update_date=latest_c)
        & Q(indicator__indicator="FUND_CORP_FUNDMANAGEMENTCOMPANY")
    ).values_list('windcode', 'indicator__text').distinct()
    all_funds1 = pd.DataFrame(all_funds1, columns=['windcode', 'name']).set_index('windcode')
    all_funds2 = models.Fund.objects.filter(
        Q(indicator__update_date=latest_i) & Q(classify__update_date=latest_c)
        & Q(indicator__indicator="FUND_FUNDSCALE")
    ).values_list('windcode', 'indicator__numeric').distinct()
    all_funds2 = pd.DataFrame(all_funds2, columns=['windcode', 'value']).set_index('windcode')
    data = pd.merge(all_funds1, all_funds2, left_index=True, right_index=True, how='inner').fillna(0)
    data = data.groupby('name').sum().sort_values(by='value', ascending=False)
    corps = data['value']
    corps = corps[: floor(len(corps) * level)]
    funds = ins.objects.filter(
        Q(indicator="FUND_CORP_FUNDMANAGEMENTCOMPANY") & Q(windcode__in=funds)
    ).values_list('windcode', 'text')
    funds = {x[0] for x in funds if x[1] in corps.index}
    return funds


def manager_working_years(funds, year):
    """基金经历工作年满？年"""
    ins = models.Indicator
    latest = latest_day_in_indicators()
    funds = ins.objects.filter(
        Q(update_date=latest) & Q(indicator="FUND_MANAGER_MANAGERWORKINGYEARS")
        & Q(windcode__in=funds)
    ).values_list('windcode', 'numeric')
    funds = [(x[0], x[1] or 0) for x in funds]
    funds = {x[0] for x in funds if x[1] >= year}
    return funds


def manager_working_years_on_this_fund(funds, year):
    """基金经历在本基金任职年限超过？年"""
    ins = models.Indicator
    latest = latest_day_in_indicators()
    funds = ins.objects.filter(
        Q(update_date=latest) & Q(indicator="FUND_MANAGER_ONTHEPOSTDAYS") & Q(windcode__in=funds)
    ).values_list('windcode', 'numeric')
    funds = [(x[0], x[1] or 0) for x in funds]
    funds = {x[0] for x in funds if x[1] / 365 >= year}
    return funds


def manager_geometry_return(funds, annual_return):
    """基金经历年化回报"""
    ins = models.Indicator
    latest = latest_day_in_indicators()
    funds = ins.objects.filter(
        Q(update_date=latest) & Q(indicator="FUND_MANAGER_GEOMETRICANNUALIZEDYIELD") & Q(windcode__in=funds)
    ).values_list('windcode', 'numeric')
    funds = [(x[0], x[1] or 0) for x in funds]
    funds = {x[0] for x in funds if x[1] >= annual_return}
    return funds


def manager_return_on_this_fund(funds, annual_return):
    """任职本基金年化回报"""
    ins = models.Indicator
    latest = latest_day_in_indicators()
    funds = ins.objects.filter(
        Q(update_date=latest) & Q(indicator="NAV_PERIODICANNUALIZEDRETURN") & Q(windcode__in=funds)
    ).values_list('windcode', 'numeric')
    funds = [(x[0], x[1] or 0) for x in funds]
    funds = {x[0] for x in funds if x[1] >= annual_return}
    return funds


def wind_rating(funds, rating=3):
    """Wind评级超过？星，默认大于等于3星"""
    ins = models.Indicator
    latest = latest_day_in_indicators()
    funds = ins.objects.filter(
        Q(update_date=latest) & Q(indicator="RATING_WIND3Y") & Q(windcode__in=funds)
    ).values_list('windcode', 'numeric')
    funds = [(x[0], x[1] or 0) for x in funds]
    funds = {x[0] for x in funds if x[1] >= rating}
    return funds


def recent_years_over_others(funds, year, level):
    """最近X年收益均超过？%分位"""
    f = funds
    ins = models.Indicator
    latest = latest_day_in_indicators()
    funds = ins.objects.filter(
        Q(update_date=latest) & Q(indicator="RETURN") & Q(note=str(year))
    ).values_list('windcode', 'numeric')
    funds = [(x[0], x[1] or 0) for x in funds]
    funds = [(x[0], x[1]) for x in funds]
    funds = sorted(funds, key=lambda x: x[1], reverse=True)
    funds = funds[: floor(len(funds) * level)]
    funds = {x[0] for x in funds}
    funds = {x for x in f if x in funds}
    return funds


def execute_basic_filter(data):
    """执行简单的筛选规则，传入参数为前端POST请求参数"""
    if data["classify"]:
        classify = [x.split("-")[-1] for x in data["classify"]]
        funds = funds_by_classify(classify)
    else:
        return -1
    if data["lever"]:
        funds = lever(funds, data["lever"])
    if data["regularOpen"]:
        funds = regular_open(funds, data["regularOpen"])
    if data["existYear"]:
        funds = fund_years(funds, data["existYear"])
    if data["netValue"]:
        funds = net_asset(funds, data["netValue"], data["netValue"])
    if data["singleHolder"]:
        funds = single_hold_shares(funds, data["singleHolder"])
    if data["organizationHolder"]:
        funds = organization_hold_shares(funds, data["organizationHolder"])
    if data["overIndex"]:
        funds = over_index_return(funds, data["overIndex"], data["existYear"])
    if data["overBench"] == "是":
        funds = over_bench_return(funds, data["existYear"])
    if data["monthWin"]:
        funds = month_win_ratio(funds, data["existYear"], data["monthWin"])
    if data["maxDownside"]:
        funds = max_downside_over_average(funds, data["existYear"], data["maxDownside"])
    if data["stdev"]:
        funds = stdev_yearly_over_range(funds, data["existYear"], data["stdev"])
    return funds


def execute_advance_filter(funds, f):
    """执行高级筛选功能，需要筛选规则f"""
    if f["overCorps"]:
        funds = corp_scale_level(funds, f["overCorps"])
    if f["workYear"]:
        funds = manager_working_years(funds, f["workYear"])
    if f["workOnThis"]:
        funds = manager_return_on_this_fund(funds, f["workOnThis"])
    if f["geoReturn"]:
        funds = manager_geometry_return(funds, f["geoReturn"] * 100)
    if f["thisReturn"]:
        funds = manager_return_on_this_fund(funds, f["thisReturn"] * 100)
    if f["windRating"]:
        funds = wind_rating(funds, f["windRating"])
    if f["recentLevel"]:
        levels = f["recentLevel"]
        for level in levels:
            level = level[1: -1]
            year, level = level.split(", ")
            level = level.split("/")
            funds = recent_years_over_others(funds, int(year), float(level[0]) / float(level[1]))
    return funds


# def basic_info(funds, page):
#     """获取基金基础信息"""
#     update_date = latest_day_in_classify()
#     ret = db.session.query(
#         Classify.classify, Classify.branch, BasicInfo.windcode, BasicInfo.sec_name, BasicInfo.fund_benchmark,
#         BasicInfo.setup_date
#     ).join(BasicInfo, and_(Classify.windcode == BasicInfo.windcode)).filter(
#         Classify.update_date == update_date, BasicInfo.windcode.in_(funds)).paginate(page, 25)
#     return ret


def fund_details(request, cls, funds, filters, page=None):
    """
    基金详细信息
    :param request: Django Rest 请求
    :param cls: APIViews
    :param page: 后端分页面
    :param funds: 基金列表
    :param filters: 筛选规则
    :return: 基金详细信息
    """
    date = latest_day_in_indicators()
    year = filters['existYear'] if filters['existYear'] else 1
    rpt = models.Indicator.objects.filter(update_date=date).order_by('-rpt_date').values_list('rpt_date').distinct()[0][
        0]
    names = models.BasicInfo.objects.filter(windcode__in=funds).values_list(
        'windcode', 'sec_name', 'setup_date').distinct()
    if page:
        paginator = PageNumberPagination()
        paginator.page_size = 50
        total = names.count()
        p = paginator.paginate_queryset(names, request, cls)
        names = p
        page = paginator.page.number
        per_page = 50
    else:
        page = None
        per_page = None
        total = None
    names = {x[0]: (x[1], x[2]) for x in names}
    data = models.Indicator.objects.filter(
        Q(update_date=date) & Q(windcode__in=names.keys()) & Q(note=year) | Q(note__isnull=True) & Q(rpt_date=rpt)
    ).values('windcode', 'indicator', 'numeric', 'text')
    codes = list({x['windcode'] for x in data})
    ret = {x: {} for x in codes}
    sp = {}
    for x in data:
        if x["windcode"] in (names.keys()):
            ret[x["windcode"]][x["indicator"]] = round(float(x["numeric"]), 2) if x["numeric"] else x['text']
            ret[x["windcode"]]["sec_name"] = names[x["windcode"]][0]
            ret[x["windcode"]]["setup"] = names[x["windcode"]][1].strftime("%Y/%m/%d")
            sp[x['windcode']] = ret[x['windcode']]
    ret = [
        {
            "windCode": x, "corp": y["FUND_CORP_FUNDMANAGEMENTCOMPANY"],
            "winRatio": y["ABSOLUTE_UPDOWNMONTHRATIO"],
            "scale": y["FUND_FUNDSCALE"] / 1e8 if y["FUND_FUNDSCALE"] else y["FUND_FUNDSCALE"],
            "managerAnnualReturn": y["FUND_MANAGER_GEOMETRICANNUALIZEDYIELD"],
            "workingYears": y["FUND_MANAGER_MANAGERWORKINGYEARS"],
            "workingOnThis": round(y["FUND_MANAGER_ONTHEPOSTDAYS"] / 365, 2),
            "singleHold": y["HOLDER_SINGLE_TOTALHOLDINGPCT"],
            "overBench": y["NAV_OVER_BENCH_RETURN_PER"],
            "workingAnnualReturn": y["NAV_PERIODICANNUALIZEDRETURN"],
            "netAsset": y["PRT_FUNDNETASSET_TOTAL"],
            "rating": int(y["RATING_WIND3Y"]) if y["RATING_WIND3Y"] else y["RATING_WIND3Y"],
            "return": (pow(1 + y["RETURN"] / 100, 1 / year) - 1) * 100 if y["RETURN"] else None,
            "maxDownSide": y["RISK_MAXDOWNSIDE"],
            "secName": y["sec_name"],
            "existYear": year,
            "setup": y["setup"],
            "update": date.strftime("%Y/%m/%d")
        }
        for x, y in sp.items()]

    return ret, page, per_page, total


def fund_details_to_excel(funds, filters):
    data, *_ = fund_details(funds, filters)
    data = pd.DataFrame(data)
    data.to_excel("./back_server/static/筛选结果.xlsx")
