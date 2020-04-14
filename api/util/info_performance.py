import datetime

import pandas as pd
import numpy as np

from dateutil.relativedelta import relativedelta


class Date(object):
    """日期处理函数"""
    @staticmethod
    def one_week(day):
        """指定日期一周前"""
        date = day + relativedelta(weeks=-1)
        return date

    @staticmethod
    def one_month(day):
        """指定日期前一月"""
        date = day + relativedelta(months=-1)
        return date

    @staticmethod
    def three_month(day):
        """指定日期前3月"""
        date = day + relativedelta(months=-3)
        return date

    @staticmethod
    def six_month(day):
        """指定日期前6月"""
        date = day + relativedelta(months=-6)
        return date

    @staticmethod
    def one_year(day):
        """指定日期前6月"""
        date = day + relativedelta(years=-1)
        return date

    @staticmethod
    def three_year(day):
        """指定日期前6月"""
        date = day + relativedelta(years=-1)
        return date

    @staticmethod
    def year_start(day):
        """指定日期前6月"""
        date = datetime.date(day.year, 1, 1)
        return date


class Performance(object):
    """计算一个series的表现"""
    def __init__(self, data):
        self.d = data
        self.t = data.index[-1]

    def compute(self, func):
        """输入一个返回事件的函数来获取期间涨跌幅"""
        w1 = func(self.t)
        n = self.d.values[-1]
        d = self.d[self.d.index <= w1].values
        if len(d) == 0:
            return None
        d = d[-1]
        ret = round((n / d - 1) * 100, 2)
        return ret

    def return_1w(self):
        ret = self.compute(Date.one_week)
        return ret

    def return_1m(self):
        ret = self.compute(Date.one_month)
        return ret

    def return_3m(self):
        ret = self.compute(Date.three_month)
        return ret

    def return_6m(self):
        ret = self.compute(Date.six_month)
        return ret

    def return_1y(self):
        ret = self.compute(Date.one_year)
        return ret

    def return_3y(self):
        ret = self.compute(Date.three_year)
        return ret

    def return_ytd(self):
        ret = self.compute(Date.year_start)
        return ret

    def return_std(self):
        s = self.d.values[0]
        n = self.d.values[-1]
        ret = None
        if s and n:
            ret = round((n/s-1)*100, 2)
        return ret


class PerformanceAll(object):
    """计算一个DataFrame的表现"""
    def __init__(self, data):
        self.d = data
        self.t = data.index[-1]

    def compute(self,  func):
        start = func(self.t)
        n = self.d.iloc[-1, :]
        d = self.d[self.d.index <= start]
        if d.empty:
            ret = pd.Series([None]*3)
            ret.index = ['fund', 'style', 'benchmark']
            return ret
        d = d.iloc[-1, :]
        ret = np.round((n/d-1)*100, 2)
        return ret

    def m3(self):
        ret = self.compute(Date.three_month)
        ret.name = 'm3'
        return ret

    def m6(self):
        ret = self.compute(Date.six_month)
        ret.name = 'm6'
        return ret

    def y1(self):
        ret = self.compute(Date.one_year)
        ret.name = 'y1'
        return ret

    def y3(self):
        ret = self.compute(Date.three_year)
        ret.name = 'y3'
        return ret

    def ytd(self):
        ret = self.compute(Date.year_start)
        ret.name = 'ytd'
        return ret

    def total(self):
        d = self.d
        d = d.fillna(method='ffill')
        ret = np.round((d.iloc[-1, :]/d.iloc[0, :]-1)*100, 2)
        ret.name = 'total'
        return ret

    def annual(self):
        ret = self.total()
        ret = np.power(1+ret/100, 250/len(self.d))-1
        ret = round(ret*100, 2)
        ret.name = 'annual'
        return ret


class YearlyPerformance(object):
    """年度表现"""
    def __init__(self, data):
        self.d = data
        self.t = data.index[-1]

    def x_year_ago(self, x):
        this_year = self.t.year
        start = datetime.date(this_year - x, 1, 1)
        if x == 0:
            end = self.t
            if self.d.index[0] >= start:
                start = self.d.index[0]
        else:
            end = datetime.date(this_year-x, 12, 31)
        return start, end

    def compute(self, x):
        start, end = self.x_year_ago(x)
        d_e = self.d[self.d.index <= end]
        if d_e.empty:
            return pd.Series([None]*3, index=['fund', 'style', 'benchmark'], name=end.year if x != 0 else 'ytd')
        d_s = self.d[self.d.index <= start]
        if d_s.empty:
            return pd.Series([None]*3, index=['fund', 'style', 'benchmark'], name=end.year if x != 0 else 'ytd')
        s = d_s.iloc[-1, :]
        e = d_e.iloc[-1, :]
        ret = np.round((e/s-1)*100, 2)
        if x == 0:
            ret.name = 'ytd'
        else:
            ret.name = end.year
        return ret
