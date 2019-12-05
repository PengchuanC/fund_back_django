from rest_framework.views import APIView
from rest_framework.response import Response

from api import util


class FilterViews(APIView):
    def post(self, request):
        funds = util.filters.execute_basic_filter(request.data)
        return Response({'data': funds})


class AdvanceViews(APIView):
    def post(self, request):
        data = request.data
        funds = data['funds']
        f = data["filter"]
        funds = util.filters.execute_advance_filter(funds, f)
        return Response({"data": list(funds)})


class FilterBasicInfoViews(APIView):
    def post(self, request):
        data = request.data
        funds = data["funds"]
        page = data["page"]
        _filters = data["filter"]
        data, page, per_page, total = util.filters.fund_details(request, self, funds, _filters, page)
        return Response({"data": data, "page": page, "total": total, "per_page": per_page})


class InfoResultViews(APIView):
    def post(self, request):
        data = request.data
        funds = data["funds"]
        _filters = data["filter"]
        util.filters.fund_details_to_excel(funds, _filters)
        return {'message': "OK", "url": "api/v1/filter/info/results"}