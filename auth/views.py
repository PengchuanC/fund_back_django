from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

# Create your views here.


class UserViews(APIView):
    def get(self, request):
        username = request.query_params.get('username')
        password = request.query_params.get('password')
        user = User.objects.check(username=username)
        if user:
            return Response({'status': 'username has been used by another user', 'code': 1})
        User.objects.create(username=username, password=password)
        return Response({'status': 'success', 'code': 0})

    def put(self, request):
        username = request.query_params.get('username')
        password = request.query_params.get('password')
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        return Response({'status': 'success', 'code': 0})
