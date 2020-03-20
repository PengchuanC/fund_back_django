import pandas as pd

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
    """基金分类概况"""
    latest_cls = util.latest(models.Classify)
    latest_ind = util.latest(models.Indicator)
    funds = models.BasicInfo.objects.filter(setup_date__lte=latest_cls).values_list('windcode').distinct()
    funds = list({x[0] for x in funds})
    data = models.Indicator.objects.filter(
        Q(windcode__in=funds) & Q(indicator='NETASSET_TOTAL') & Q(update_date=latest_ind)).values_list(
        'windcode', 'numeric', 'windcode__basicinfo__fullname'
    ).distinct()
    data = pd.DataFrame(data, columns=['windcode', 'scale', 'fullname'])
    classify = models.Classify.objects.filter(update_date=latest_cls).values_list('windcode', 'branch', 'classify')
    classify = pd.DataFrame(classify, columns=['windcode', 'branch', 'classify'])
    data = data.drop_duplicates('windcode')
    t_c = len(data)
    data_dd = data.drop_duplicates('fullname')
    t_s = round(data_dd['scale'].sum()/1e8, 0)
    t_c_dd = len(data_dd)
    branch = set(list(classify['branch']))
    b_ret, c_ret = [], []
    for b in branch:
        b_data = data[data['windcode'].isin(classify[classify['branch'] == b]['windcode'])]
        b_c = len(b_data)
        b_data_dd = b_data.drop_duplicates('fullname')
        b_s = round(b_data_dd['scale'].sum()/1e8, 0)
        b_c_dd = len(b_data_dd)
        children = []
        b_ret.append({"branch": b, 'count': b_c, 'count2': b_c_dd, 'scale': b_s, "children": children})
        clas = set(list(classify[classify['branch'] == b]['classify']))
        for c in clas:
            c_data = b_data[b_data['windcode'].isin(classify[(classify['branch'] == b) & (classify['classify'] == c)]['windcode'])]
            c_c = len(c_data)
            c_data_dd = c_data.drop_duplicates('fullname')
            c_s = round(c_data_dd['scale'].sum() / 1e8, 0)
            c_c_dd = len(c_data_dd)
            children.append({"branch": b, "classify": c, "count": c_c, 'count2': c_c_dd, "scale": c_s})
    b_ret = sorted(b_ret, key=lambda x: x['scale'], reverse=True)
    b_ret_m = []
    for ret in b_ret:
        ret['children'] = sorted(ret['children'], key=lambda x: x['scale'], reverse=True)
        b_ret_m.append(ret)
    return {"total": {"count": t_c, 'count2': t_c_dd, "scale": t_s}, "branch": b_ret_m, 'date': latest_cls}
