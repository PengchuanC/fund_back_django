from datetime import timedelta
from functools import lru_cache
from math import floor, pow

import pandas as pd

from django.db.models import Q
from django.db import connection
from rest_framework.pagination import PageNumberPagination

from api import models, util


def funds_by_classify(cls: list):
    """获取特定分类下的全部基金"""
    return util.filters.funds_by_classify(cls)


def lever(funds, yes_or_no):
    """是否是杠杆基金"""
    return util.filters.lever(funds, yes_or_no)


def fund_years(funds, left, right=50):
    """基金存续时间位于[left, right]"""
    return util.filters.fund_years(funds, left, right)


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