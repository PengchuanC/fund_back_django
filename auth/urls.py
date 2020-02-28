from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from auth import views


urlpatterns = [
    url(r'auth/', views.UserViews.as_view()),
    url(r'login/', obtain_jwt_token)
]
