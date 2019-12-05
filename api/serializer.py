from rest_framework import serializers

from api import models


class FundSerializer(serializers.ModelSerializer):
    windcode = serializers.CharField(max_length=12)
    category = serializers.IntegerField()

    class Meta:
        model = models.Fund
        fields = "__all__"


class StyleSerializer(serializers.ModelSerializer):
    windcode = serializers.CharField()
    small_value = serializers.FloatField()
    small_growth = serializers.FloatField()
    mid_value = serializers.FloatField()
    mid_growth = serializers.FloatField()
    large_value = serializers.FloatField()
    large_growth = serializers.FloatField()
    bond = serializers.FloatField()
    r_square = serializers.FloatField()
    value_date = serializers.DateField()
    freq = serializers.CharField(max_length=2)

    class Meta:
        model = models.Style
        fields = '__all__'


class ManagerSerializer(serializers.ModelSerializer):
    windcode = serializers.CharField()
    fund_fundmanager = serializers.CharField()
    fund_predfundmanager = serializers.CharField()
    fund_corp_fundmanagementcompany = serializers.CharField()
    update_date = serializers.DateField()

    class Meta:
        model = models.Manager
        fields = '__all__'


class ManagerExpandSerializer(serializers.ModelSerializer):
    windcode = ManagerSerializer
    fund_manager_totalnetasset = serializers.FloatField()
    fund_manager_resume = serializers.CharField()
    fund_manager_gender = serializers.CharField()
    nav_periodicannualizedreturn = serializers.FloatField()
    rank = serializers.IntegerField()
    update_date = serializers.DateField()

    class Meta:
        model = models.ManagerExpand
        fields = '__all__'


class BrinsonSerializer(serializers.ModelSerializer):
    windcode = serializers.CharField()
    industry_code = serializers.CharField()
    industry_name = serializers.CharField()
    q1 = serializers.FloatField()
    q2 = serializers.FloatField()
    q3 = serializers.FloatField()
    q4 = serializers.FloatField()
    raa = serializers.FloatField()
    rss = serializers.FloatField()
    rin = serializers.FloatField()
    rto = serializers.FloatField()
    freq = serializers.CharField()
    benchmark = serializers.CharField()
    rpt_date = serializers.DateField()

    class Meta:
        model = models.Brinson
        fields = '__all__'
