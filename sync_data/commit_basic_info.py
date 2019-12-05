import pandas as pd

from sync_data.session import default_engine
from api.models import BasicInfo, Fund

conn = default_engine()

windcode = Fund.objects.all().values('windcode')
codes = [x['windcode'] for x in windcode]
data = pd.read_sql("select * from t_ff_basic_info;", con=conn)
data = data.drop("id", axis=1)
data = data.drop_duplicates()
data = data.to_dict(orient="records")
basic_info = [BasicInfo(
    windcode_id=x['windcode'], sec_name=x['sec_name'], fullname=x['fund_fullname'], setup_date=x['fund_setupdate'],
    benchmark=x['fund_benchmark'], company=x['fund_fundmanagementcompany'], invest_scope=x['fund_investscope'],
    structured=0 if x['fund_structuredfundornot'] == "是" else 1,
    first_invest_type=x['fund_firstinvesttype'], invest_type=x['fund_investtype'], update_date=x['update_date']
) for x in data if x['windcode'] in codes]

BasicInfo.objects.bulk_create(basic_info)
