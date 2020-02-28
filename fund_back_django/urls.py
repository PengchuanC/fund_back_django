from django.contrib import admin
from django.urls import path, include
# from rest_framework_jwt.views import obtain_jwt_token,verify_jwt_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/news/', include('news.urls')),
    path('api/v1/', include('api.urls')),
    # path('auth/', obtain_jwt_token),
    # path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
