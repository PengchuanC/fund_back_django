import datetime

from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from news.models import News
from news.serializer import NewsSerializer


class Breaking(APIView):
    def get(self, request):
        queryset = News.objects.all()
        paginator = PageNumberPagination()
        paginator.page_query_param = "page_num"
        ret = paginator.paginate_queryset(queryset, request, self)
        ret = NewsSerializer(ret, many=True)
        return Response({"data": ret.data, "page": paginator.page.number, "per_page": paginator.page_size, "total": queryset.count()})


@api_view(['GET'])
def following_keywords(request):
    queryset = News.objects.all().filter(keyword__isnull=False).values('keyword').distinct()
    ret = {x['keyword'] for x in queryset}
    return Response(ret)


class NewsList(APIView):
    def get(self, request):
        args = request.query_params
        date = args.get("date", None)
        search = args.get("search", None)
        section = args.get("section", None)

        queryset = News.objects
        if date:
            start = datetime.datetime.strptime(date[:10], '%Y-%m-%d')
            end = start + datetime.timedelta(days=1)
            queryset = queryset.filter(savedate__range=(start, end))
        if search:
            queryset = queryset.filter(Q(title__contains=search) | Q(abstract__contains=search))
        if section and section != 'whole':
            sections = {"economy": "宏观", "finance": "金融", "company": "商业", "japan": "日本"}
            queryset = queryset.filter(keyword=sections[section])
        queryset = queryset.all().order_by('-id')

        paginator = PageNumberPagination()
        paginator.page_query_param = "page"

        ret = paginator.paginate_queryset(queryset, request, self)
        ret = NewsSerializer(ret, many=True)
        return Response({"data": ret.data, "page": paginator.page.number, "per_page": paginator.page_size,
                         "total": queryset.count()})
