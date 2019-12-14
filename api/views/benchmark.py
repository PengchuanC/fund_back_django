from rest_framework.views import APIView
from rest_framework.response import Response

from api import util, models


class BenchmarkNameViews(APIView):
    def get(self, request):
        queryset = models.Index.objects.filter(kind='normal').values('windcode', 'sec_name')
        return Response(queryset)
