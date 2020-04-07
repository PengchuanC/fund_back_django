from WindPy import w

import sync_data

from api.models import Fund


w.start()
DATE = "2020-03-31"


funds_in_mysql = Fund.objects.filter(category=1).all()

err, funds_in_wind = w.wset(
    "sectorconstituent", f"date={DATE};sectorid=a201010400000000", usedf=True
)
funds_in_wind = list(funds_in_wind["wind_code"])


need_delete = [x for x in funds_in_mysql if x.windcode not in funds_in_wind]
for x in need_delete:
    x.delete()