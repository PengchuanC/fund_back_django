from datetime import date

from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, Min, Max

import pandas as pd
import numpy as np

from api import util
from api import models
from api import serializer


class PerformanceViews(APIView):
    def get(self, request):
        windcode = request.query_params.get('windcode', '000001.OF')
        fp = models.FundPerformance.objects
        sec_name = models.BasicInfo.objects.filter(windcode=windcode).first().sec_name
        latest = util.latest(models.FundPerformance)
        ret = fp.filter(Q(windcode=windcode) & Q(update_date=latest)).all()
        data = {"update_date": latest.strftime("%Y-%m-%d"), "sec_name": sec_name}
        for r in ret:
            data[r.indicator] = r.value
        latest = models.FundNav.objects.filter(Q(windcode=windcode)).aggregate(Max('date'))['date__max']
        nav_latest = models.FundNav.objects.filter(Q(windcode=windcode) & Q(date=latest)).values('nav', 'nav_adj').first()
        nav = models.FundNav.objects.filter(Q(windcode=windcode)).order_by('date').values('date', 'nav_adj')
        nav = pd.DataFrame(nav).set_index('date')['nav_adj']
        print(nav_latest)
        ret = {'update_date': latest.strftime("%Y-%m-%d"), "NAV": nav_latest['nav'], 'NAV_ACC': nav_latest['nav_adj']}
        p = util.Performance(nav)
        for key in [
            'return_1w', 'return_1m', 'return_3m', 'return_6m', 'return_1y', 'return_3y', 'return_ytd', 'return_std'
        ]:
            ret[key.upper()] = getattr(p, key)()
        return Response(ret)


class StyleViews(APIView):
    def get(self, request):
        windcode = request.query_params.get('windcode', '000001.OF')
        ret = models.Style.objects.filter(windcode=windcode).all()
        serialized = serializer.StyleSerializer(ret, many=True)
        return Response(serialized.data)


class StyleAndBenchmarkViews(APIView):
    def get(self, request):
        benchmark = models.Index.objects.filter(kind='normal').values_list('windcode', 'sec_name')
        style = models.Index.objects.filter(kind='invest_style').values_list('windcode', 'sec_name')
        return Response({"benchmark": benchmark, "style": style})


class PlotPerformanceViews(APIView):
    def post(self, request):
        return Response(PlotPerformanceViews.compute(request))

    @staticmethod
    def compute(request):
        """整理基金业绩表现数据，附带股票指数和行业指数"""
        params = request.data
        windcode = params.get("windcode")
        is_in = models.FundNav.objects.filter(windcode=windcode).first()
        if not is_in:
            return {"msg": -1, "info": f"{windcode} is not in FundNav"}
        name = models.BasicInfo.objects.filter(windcode=windcode).first().sec_name
        style = params.get("style")
        benchmark = params.get("benchmark")

        latest = util.latest(models.Classify)
        branch = models.Classify.objects.filter(Q(update_date=latest) & Q(windcode=windcode)).first().branch

        if not benchmark:
            basic_benchmark = {
                "股票类": "000906.SH", "债券类": "CBA00301.CS", "货币类": "H11025.CSI",
                "另类": "000001.SH", "QDII": "000300.SH", "FOF": "000300.SH"
            }
            benchmark = basic_benchmark.get(branch, "8000300.SH")
        benchmark_name = models.Index.objects.filter(windcode=benchmark).first().sec_name
        if not style:
            basic_style = {"股票类": "885012.WI", "债券类": "885005.WI", "货币类": "885009.WI",
                           "另类": "885010.WI", "QDII": "885054.WI", "FOF": "885010.WI"}
            style = basic_style.get(branch, "885010.WI")
        style_name = models.Index.objects.filter(windcode=style).first().sec_name
        start = models.FundNav.objects.filter(windcode=windcode).aggregate(Min('date')).get('date__min')
        nav_adj = models.FundNav.objects.filter(Q(windcode=windcode) & Q(date__gte=start)).values_list(
            'nav_adj', 'date'
        )
        style_cp = models.IndexClosePrice.objects.filter(Q(windcode=style) & Q(date__gte=start)).values_list(
            'close', 'date'
        )
        bench_cp = models.IndexClosePrice.objects.filter(Q(windcode=benchmark) & Q(date__gte=start)).values_list(
            'close', 'date'
        )
        nav_adj = pd.DataFrame(nav_adj, columns=['fund', 'date']).set_index("date")
        style_cp = pd.DataFrame(style_cp, columns=['style', 'date']).set_index("date")
        bench_cp = pd.DataFrame(bench_cp, columns=['benchmark', 'date']).set_index("date")
        data = pd.merge(nav_adj, style_cp, how="left", left_index=True, right_index=True)
        data = pd.merge(data, bench_cp, how="left", left_index=True, right_index=True)
        data.columns = ["fund", "style", "benchmark"]

        performance = PlotPerformanceViews.performance(data)
        performance["name"] = [name, style_name, benchmark_name]
        performance = performance.to_dict(orient="records")

        year_performance = PlotPerformanceViews.yearly_performance(data)
        yp_t = year_performance.T
        year_performance["name"] = [name, style_name, benchmark_name]
        yp_t.columns = [name, style_name, benchmark_name]
        yp_t["year"] = yp_t.index
        year_performance_chart = yp_t.to_dict(orient="records")
        year_performance = year_performance.to_dict(orient="records")

        data = data.fillna(method="bfill")
        data = data / data.iloc[0, :] - 1
        data = data.apply(lambda x: round(x, 4))
        data["date"] = data.index
        data["date"] = data["date"].apply(lambda x: x.strftime("%Y-%m-%d"))
        data = data.to_dict(orient="list")
        ret = {"data": data, "fund": name, "style": style_name, "benchmark": benchmark_name,
                "performance": performance, "yearly": year_performance, "yearly_chart": year_performance_chart,
                "msg": 0}
        return ret

    @staticmethod
    def performance(data: pd.DataFrame):
        """|index|fund|style|benchmark|"""
        data = data.fillna(method='bfill')
        dates = list(data.index)
        table = pd.DataFrame()
        date = dates[-1]
        du = util.DateUtil(date)
        ytd = du.ytd()
        end = -1
        start = 0
        if ytd not in dates:
            table['ytd'] = not_in_series()
        else:
            ytd = dates.index(ytd)
            table["ytd"] = round((data.iloc[end] / data.iloc[ytd] - 1) * 100, 2)

        m3 = du.x_months_ago(3)
        if m3 not in dates:
            table['m3'] = not_in_series()
        else:
            m3 = dates.index(m3)
            table["m3"] = round((data.iloc[end] / data.iloc[m3] - 1) * 100, 2)

        m6 = du.x_months_ago(6)
        if m6 not in dates:
            table['m6'] = not_in_series()
        else:
            m6 = dates.index(m6)
            table["m6"] = round((data.iloc[end] / data.iloc[m6] - 1) * 100, 2)

        for x in [1, 2, 3, 5]:
            y = du.x_years_ago(x)
            dates_ = list(filter(lambda d: d <= y, dates))
            if not dates_:
                table[f"y{x}"] = not_in_series()
            else:
                y = dates.index(dates_[-1])
                table[f"y{x}"] = round((data.iloc[end] / data.iloc[y] - 1) * 100, 2)

        data = data.fillna(method='bfill')
        total = round((data.iloc[end] / data.iloc[start] - 1) * 100, 2)
        table["total"] = total

        annual = round((np.power(1+total/100, 365/len(dates)) - 1)*100, 2)
        table["annual"] = annual

        return table

    @staticmethod
    def yearly_performance(data):
        """|index|fund|style|benchmark|"""
        data = data[data.index >= date(date.today().year-5, 1, 1)]
        dates = list(data.index)
        start = dates[0]
        end = dates[-1]
        start_y = start.year
        end_y = end.year
        table = pd.DataFrame()
        for y in range(start_y, end_y):
            if y == start_y:
                d1 = dates.index(start)
            else:
                d1 = list(filter(lambda x: x <= date(y-1, 12, 31), dates))[-1]
                d1 = dates.index(d1)
            d2 = list(filter(lambda x: x <= date(y, 12, 31), dates))[-1]
            d2 = dates.index(d2)
            table[f"{y}"] = round((data.iloc[d2]/data.iloc[d1]-1)*100, 2)
        ytd = dates.index(date(end_y-1, 12, 31))
        table["ytd"] = round((data.iloc[-1]/data.iloc[ytd]-1)*100, 2)
        return table


def not_in_series():
    return pd.Series([None, None, None], index=["fund", "style", "benchmark"])
