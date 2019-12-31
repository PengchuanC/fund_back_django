from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, Max

import pandas as pd

from api import util, models, serializer


def product_type():
    """获取产品类型"""
    latest_public = util.latest(models.Classify)
    print(latest_public)
