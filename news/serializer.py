from rest_framework import serializers
from .models import News


class NewsSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=200)
    abstract = serializers.CharField
    url = serializers.CharField()
    source = serializers.CharField(max_length=20)
    savedate = serializers.DateTimeField()
    keyword = serializers.CharField(max_length=10)

    class Meta:
        model = News
        fields = "__all__"
