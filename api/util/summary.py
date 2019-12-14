from functools import lru_cache

from django.db.models import Q, Max

from api import models, util


def summary():
    """基金分类总结"""
    latest = util.latest(models.Classify)
    total_count = models.Classify.objects.filter(update_date=latest).values("windcode").distinct().count()
    branch = models.Classify.objects.filter(update_date=latest).values("branch").distinct()
    branch = [x['branch'] for x in branch]

    open_fund = {"name": "公募基金", "value": total_count, "children": []}
    for bran in branch:
        bran_count = models.Classify.objects.filter(
            Q(update_date=latest) & Q(branch=bran)
        ).values("classify").distinct().count()
        classify = models.Classify.objects.filter(update_date=latest).values("classify").distinct()
        classify = [x['classify'] for x in classify]
        branch_classify = {"name": bran, "value": bran_count, "children": []}
        for cla in classify:
            cla_count = models.Classify.objects.filter(
                Q(update_date=latest) & Q(branch=bran) & Q(classify=cla)
            ).values("windcode").distinct().count()
            _classify = {"name": cla, "value": cla_count}
            branch_classify["children"].append(_classify)
        open_fund["children"].append(branch_classify)
    return open_fund


def summarise():
    """基金分类概括"""
    latest_cls = util.latest(models.Classify)
    latest_ins = util.latest(models.Indicator)
    latest_rpt = models.Indicator.objects.aggregate(Max('rpt_date')).get('rpt_date__max')
    data = models.Fund.objects.filter(
        Q(classify__update_date=latest_cls) & Q(indicator__update_date=latest_ins) & Q(indicator__rpt_date=latest_rpt)
        & Q(indicator__indicator="FUND_FUNDSCALE")
    ).values_list('windcode', 'classify__branch', 'classify__classify', 'indicator__numeric').distinct()
    total = {x[0]: float(x[-1]) if x[-1] else 0 for x in data}
    t_c, t_s = len(total.keys()), format(round(sum(total.values()) / 1e8, 0), '0,.0f')

    b_ret, c_ret = [], []
    branch = set([x[1] for x in data])
    for b in branch:
        classify = set(x[2] for x in data if x[1] == b)
        b_data = {x[0]: float(x[-1]) if x[-1] else 0 for x in data if x[1] == b}
        b_c, b_s = len(b_data.keys()), format(round(sum(b_data.values()) / 1e8, 0), '0,.0f')
        children = []
        b_ret.append({"branch": b, 'count': b_c, 'scale': b_s, "children": children})
        for c in classify:
            c_data = {x[0]: float(x[-1]) if x[-1] else 0 for x in data if x[1] == b and x[2] == c}
            c_c, c_s = len(c_data.keys()), format(round(sum(c_data.values()) / 1e8, 0), '0,.0f')
            children.append({"branch": b, "classify": c, "count": c_c, "scale": c_s})
    return {"total": {"count": t_c, "scale": t_s}, "branch": b_ret}
