import pandas as pd

from sync_data.session import default_engine
from api.models import Fund, FundNav

conn = default_engine()

"""同步基金列表"""
data = pd.read_sql("select * from t_ff_funds;", con=conn)
data = data.to_dict(orient="records")
fund = [Fund(windcode=x['windcode'], category=1) for x in data]

Fund.objects.bulk_create(fund)


"""同步基金净值"""
data = pd.read_sql("select * from t_ff_fund_nav;", con=conn)
data = data.to_dict(orient="records")
fund_nav = [FundNav(windcode_id=x['windcode'], nav=x['nav'], nav_adj=x['nav_adj'], date=x['date']) for x in data]

FundNav.objects.bulk_create(fund_nav)
