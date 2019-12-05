import pandas as pd

from sync_data.session import default_engine
from api.models import Fund, Manager, ManagerExpand

conn = default_engine()

windcode = Fund.objects.all().values('windcode')
codes = [x['windcode'] for x in windcode]


"""同步manager
data = pd.read_sql("select * from t_ff_manager;", con=conn)
data = data[data.windcode.isin(codes)]
data = data.drop("id", axis=1)
data = data.drop_duplicates()
data = data.to_dict(orient="records")
manager = [Manager(
    windcode_id=x['windcode'], fund_fundmanager=x["fund_fundmanager"], fund_predfundmanager=x['fund_predfundmanager'],
    fund_corp_fundmanagementcompany=x["fund_corp_fundmanagementcompany"], update_date=x["update_date"]
) for x in data]
Manager.objects.bulk_create(manager)
"""


"""同步manager_expand"""
data = pd.read_sql("select * from t_ff_manager_expand;", con=conn)
data = data[data.windcode.isin(codes)]
data = data.drop("id", axis=1)
data = data[data["rank"].notnull()]
data = data.drop_duplicates()
data = data.to_dict(orient="records")

expand = [ManagerExpand(
    windcode_id=x['windcode'], update_date=x["update_date"],
    fund_manager_totalnetasset=x["fund_manager_totalnetasset"],
    nav_periodicannualizedreturn=x['nav_periodicannualizedreturn'], fund_manager_resume=x['fund_manager_resume'],
    fund_manager_gender=x["fund_manager_gender"], rank=x["rank"]
) for x in data if str(x["fund_manager_totalnetasset"]) != "nan"]
ManagerExpand.objects.bulk_create(expand)
