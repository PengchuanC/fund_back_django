from django.conf.urls import url

from news import views


urlpatterns = [
    url(r'breaking', views.Breaking.as_view()),
    url(r'follow/keywords', views.following_keywords),
    url(r'newslist', views.NewsList.as_view())
]
