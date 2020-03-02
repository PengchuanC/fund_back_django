import math
import datetime

import numpy as np


class Performance(object):

    def __init__(self, data):
        self.d = data.dropna(how="any")

    def r1y(self):
        t = datetime.date.today()
        date = datetime.date(t.year-1, t.month, t.day)
        d = self.d[self.d.index >= date]
        return self.term_return(d)

    def r3y(self):
        t = datetime.date.today()
        date = datetime.date(t.year - 3, t.month, t.day)
        d = self.d[self.d.index >= date]
        return self.term_return(d)

    def ytd(self):
        t = datetime.date.today()
        date = datetime.date(t.year, 1, 1)
        d = self.d[self.d.index >= date]
        return self.term_return(d)

    def sigma(self):
        chg = self.d.pct_change().dropna()
        std = chg.std()
        sigma = std * math.sqrt(52)
        return sigma

    @staticmethod
    def term_return(d):
        if d.empty:
            return None
        length = (d.index[-1] - d.index[0]).days
        if any({length == 0, d.index[0] == 0}):
            return None
        r = np.power(d[-1]/d[0], 365/length) - 1
        return r
