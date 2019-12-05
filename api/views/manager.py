from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q

from api import util, models


class ManagerViews(APIView):
    def get(self, request):
        windcode = request.query_params.get('windcode')
        scale = models.Indicator.objects.filter(Q(windcode=windcode) & Q(indicator="PRT_FUNDNETASSET_TOTAL")).order_by(
            '-rpt_date').values('numeric', 'rpt_date').first()
        ret = models.Manager.objects.filter(windcode=windcode).values_list(
            "windcode", "fund_fundmanager", "fund_predfundmanager", "fund_corp_fundmanagementcompany", 'update_date',
            "manager_info__fund_manager_totalnetasset", 'manager_info__fund_manager_resume',
            'manager_info__fund_manager_gender', 'manager_info__nav_periodicannualizedreturn'
        ).first()
        ret = {"windcdoe": ret[0], "manager": ret[1], "predmanager": ret[2], "company": ret[3], 'update_date': ret[4],
               'manager_info': [{'netasset': ret[5], 'resume': ret[6], 'gender': ret[7], 'return': ret[8]}],
               'scale': f"{round(float(scale['numeric']) / 1e8, 2)}亿元({scale['rpt_date'].strftime('%Y-%m-%d')})"}
        basic = models.Fund.objects.filter(
            Q(windcode=windcode) & Q(classify__update_date=util.latest(models.Classify))
        ).values('classify__classify', 'basicinfo__setup_date', 'basicinfo__benchmark').first()
        ret['classify'] = basic['classify__classify']
        ret['setup'] = basic['basicinfo__setup_date'].strftime('%Y-%m-%d')
        ret['bench'] = basic['basicinfo__benchmark']
        return Response(ret)


class ManagedViews(APIView):
    def get(self, request):
        name = request.query_params.get("name")
        latest = util.latest(models.Classify)
        latest_fm = util.latest(models.Manager)
        codes = models.Manager.objects.filter(fund_fundmanager__contains=name).values_list('windcode')
        name = models.BasicInfo.objects.filter(windcode__in=codes).values_list('windcode', 'sec_name')
        name = list(set(name))
        name = {x[0]: x[1] for x in name}
        cls = models.Classify.objects.filter(Q(windcode__in=codes) & Q(update_date=latest)).values_list(
            'windcode', 'classify'
        )
        cls = {x[0]: x[1] for x in cls}
        manager = models.Manager.objects.filter(Q(windcode__in=codes) & Q(update_date=latest_fm)).all()

        manager = {x.windcode.windcode: [self.split(x.fund_predfundmanager),
                                x.manager_info.all()[0].nav_periodicannualizedreturn] for x in manager}
        ret = []
        for x in name.keys():
            info = {
                "windcode": x,
                "sec_name": name[x],
                "classify": cls[x],
                "serve_date": manager[x][0],
                "return": round(manager[x][1], 2)
            }
            ret.append(info)
        return Response(ret)

    def split(self, managers):
        managers = managers.split("\r\n")
        manager = None
        for x in managers:
            if "至今" in x:
                manager = x.split("(")[1][:8]
                break
        return manager
