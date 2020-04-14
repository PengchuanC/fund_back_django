import datetime
import dateutil as du

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
    def __init__(self, data):
        self.d = data
        self.t = data.index[-1]

    def compute(self, func):
        """输入一个返回事件的函数来获取期间涨跌幅"""
        w1 = func(self.t)
        n = self.d.values[-1]
        d = self.d[self.d.index <= w1].values[-1]
        ret = None
        if n and d:
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
