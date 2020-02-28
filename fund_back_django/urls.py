from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/news/', include('news.urls')),
    path('api/v1/', include('api.urls')),
    path('auth/', include('auth.urls'))
]
