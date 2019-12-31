from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, Max

import pandas as pd

from api import util, models, serializer


class ProductTypeViews(APIView):
    def get(self, request):
        return Response(product_type())


def product_type():
    """获取产品类型"""
    latest_public = util.latest(models.Classify)
    public = models.Classify.objects.filter(update_date=latest_public).values_list("branch").distinct()
    print(public)
