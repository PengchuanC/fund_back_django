from django.db import models
from datetime import date, timedelta


def latest(model):
    queryset = model.objects.aggregate(models.Max('update_date')).get('update_date__max')
    return queryset


class DateUtil(object):
    def __init__(self, _date: date):
        self.dt = _date

    def split_date(self):
        year = self.dt.year
        month = self.dt.month
        day = self.dt.day
        return year, month, day

    def x_months_ago(self, x=1):
        y, m, d = self.split_date()
        m = m - x
        if m <= 0:
            y -= 1
            m = 12 + m
        return date(y, m, d) - timedelta(days=1)

    def x_years_ago(self, x=1):
        y, m, d = self.split_date()
        y -= x
        return date(y, m, d) - timedelta(days=1)

    def ytd(self):
        y, m, d = self.split_date()
        return date(y, 1, 1) - timedelta(days=1)