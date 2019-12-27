from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, Max

import pandas as pd

from api import util, models, serializer


class BrinsonViews(APIView):
    def get(self, request):
        args = BrinsonViews.arg_parser(request)
        if args is None:
            return
        windcode = args.get("windcode")
        benchmark = args.get("benchmark")
        freq = args.get("freq")
        rpt_date = args.get("rpt_date")
        if freq == "S":
            ret = models.Brinson.objects.filter(
                Q(rpt_date=rpt_date) & Q(freq=freq) & Q(windcode=windcode) & Q(benchmark=benchmark)
            ).order_by('industry_code').all()
        else:
            ret = multi_period(windcode, benchmark, rpt_date)
        ret = serializer.BrinsonSerializer(ret, many=True)
        return Response(ret.data)

    @staticmethod
    def arg_parser(request):
        args = request.query_params
        windcode = args.get("windcode")
        is_in = models.Brinson.objects.filter(windcode=windcode).first()
        if not is_in:
            return
        benchmark = args.get("benchmark")
        if benchmark is None:
            benchmark = "000300.SH"

        rpt_date = args.get("rpt_date")
        if rpt_date is None:
            rpt_date = models.Brinson.objects.filter(
                windcode=windcode).aggregate(Max('rpt_date')).get('rpt_date__max')
            freq = "S"
        else:
            rpt_date = rpt_date.split(",")
            if len(rpt_date) == 1:
                rpt_date = rpt_date[0]
                freq = "S"
            else:
                freq = "M"
        return {"windcode": windcode, "benchmark": benchmark, "freq": freq, "rpt_date": rpt_date}


def multi_period(windcode, benchmark, rpt_date: list):
    """多期brinson模型"""
    b = models.Brinson.objects

    data = b.filter(
        Q(rpt_date__range=(rpt_date[0], rpt_date[1])) & Q(freq="S") & Q(windcode=windcode) & Q(benchmark=benchmark)
    ).all()
    data = pd.DataFrame(data).fillna(0)
    data = data.set_index("industry_code")
    for k in ["q1", "q2", "q3", "q4"]:
        data[k] = data[k] / 100 + 1
    rpts = sorted(list(set(data["rpt_date"])), reverse=True)
    init = data[data["rpt_date"] == rpts[0]]

    for rpt in rpts[1:]:
        other = data[data["rpt_date"] == rpt]
        for k in ["q1", "q2", "q3", "q4"]:
            init[k] *= other[k]
    for k in ["q1", "q2", "q3", "q4"]:
        init[k] = (init[k] - 1)*100

    init = init.reset_index()
    init["rpt_date"] = init["rpt_date"].apply(lambda x: x.strftime("%Y-%m-%d"))

    init["raa"] = init["q2"] - init["q1"]
    init['rss'] = init["q3"] - init["q1"]
    init["rin"] = init["q4"] - init["q3"] - init["q2"] + init["q1"]
    init["rto"] = init["q4"] - init["q1"]
    return init.to_dict(orient="records")


class RptDateViews(APIView):
    def get(self, request):
        windcode = request.query_params.get('windcode')
        branch = FundBranchViews.branch(windcode)['branch']
        if branch == "债券类":
            dates = models.BondStyle.objects.filter(windcode=windcode).order_by(
                '-value_date'
            ).values_list('value_date').distinct()
            dates = [x[0].strftime("%Y-%m-%d") for x in dates]
            return Response({'date': dates})
        is_in = models.Brinson.objects.filter(windcode=windcode).values('windcode').first()
        if not is_in:
            return
        dates = models.Brinson.objects.filter(
            Q(windcode=windcode) & Q(freq="S") & Q(benchmark="000300.SH")
        ).order_by('-rpt_date').values_list('rpt_date').distinct()
        dates = [x[0].strftime("%Y-%m-%d") for x in dates]
        benchs = models.Brinson.objects.filter(
            Q(rpt_date=dates[0]) & Q(windcode=windcode) & Q(freq="S")
        ).values_list('benchmark').distinct()[0]
        return Response({"date": dates, "benchmark": benchs})


class FundBranchViews(APIView):
    def get(self, request):
        windcode = request.query_params.get('windcode')
        queryset = FundBranchViews.branch(windcode)
        return Response(queryset)

    @staticmethod
    def branch(windcode):
        latest = util.latest(models.Classify)
        queryset = models.Classify.objects.filter(Q(windcode=windcode) & Q(update_date=latest)).values('branch').first()
        return queryset


class BondAttributionViews(APIView):
    def get(self, request):
        windcode = request.query_params.get('windcode')
        table = models.BondStyle.objects.filter(
            Q(windcode=windcode)
        ).order_by('-value_date').values(
            'value_date', 'short', 'long', 'conver', 'cre_short', 'cre_medium', 'cre_long', 'interest'
        )
        table = self.format_table(table)
        return Response({'table': table})

    def format_table(self, data):
        ret = []
        for l in data:
            d = {}
            for k, v in l.items():
                if isinstance(v, float):
                    d[k] = round(v, 4)
                else:
                    d[k] = v
            ret.append(d)
        return ret
