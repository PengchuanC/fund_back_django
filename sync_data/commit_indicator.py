import pandas as pd

from sync_data.session import default_engine
from api.models import Fund, Indicator, IndicatorForPlot, Index, IndicatorIndex

conn = default_engine()

windcode = Fund.objects.all().values('windcode')
codes = [x['windcode'] for x in windcode]

"""同步filter"""
data = pd.read_sql("select * from t_ff_indicator_for_filter where update_date > '2019-09-30';", con=conn)
data = data[data.windcode.isin(codes)]
data = data.drop("id", axis=1)
data = data.drop_duplicates()
data = data.to_dict(orient="records")
for_filter = [Indicator(
    windcode_id=x['windcode'], indicator=x['indicator'], numeric=x['numeric'] if str(x['numeric']) != "nan" else None, text=x['text'], note=x['note'],
    rpt_date=x['rpt_date'], update_date=x['update_date']
) for x in data]
Indicator.objects.bulk_create(for_filter)

"""同步plot
data = pd.read_sql("select * from t_ff_indicator_for_plot;", con=conn)
data = data[data.windcode.isin(codes)]
data = data.drop("id", axis=1)
data = data.drop_duplicates()
print(data.columns)
data = data.to_dict(orient="records")
for_plot = [IndicatorForPlot(
    windcode_id=x['windcode'], fund_setupdate=x['fund_setupdate'],
    fund_corp_fundmanagementcompany=x['fund_corp_fundmanagementcompany'],
    prt_netasset=x['prt_netasset'] if str(x['prt_netasset'])  != 'nan' else None,
    rpt_date=x['rpt_date'], update_date=x['update_date'],
    fund_fundscale=x['fund_fundscale'] if str(x['fund_fundscale']) != 'nan' else None
) for x in data]
IndicatorForPlot.objects.bulk_create(for_plot)
"""


# windcode = Index.objects.all().values('windcode')
# codes = [x['windcode'] for x in windcode]
# codes = "'" + "','".join(codes) + "'"
# data = pd.read_sql(f"select * from t_ff_indicator_for_filter where windcode in ({codes});", con=conn)
# print(data)
# try:
#     data = data.drop("id", axis=1)
# except KeyError:
#     pass
# try:
#     data = data[data.windcode.isin(codes)]
#     data = data.rename(columns={'windcode': 'windcode'})
# except AttributeError:
#     pass
# data = data.drop_duplicates()
# data = data.to_dict(orient="records")
#
# ret = []
# for x in data:
#     for k, v in x.items():
#         if str(v) == "nan":
#             x.update({k: None})
#     ret.append(IndicatorIndex(**x))
#
# IndicatorIndex.objects.bulk_create(ret)data = pd.read_sql(f"select * from t_ff_indicator_for_filter;", con=conn)
# try:
#     data = data.drop("id", axis=1)
# except KeyError:
#     pass
# try:
#     data = data[data.windcode.isin(codes)]
#     data = data.rename(columns={'windcode': 'windcode'})
# except AttributeError:
#     pass
# data = data.drop_duplicates()
# data = data.to_dict(orient="records")
#
# ret = []
# for x in data:
#     for k, v in x.items():
#         if str(v) == "nan":
#             x.update({k: None})
#     ret.append(IndicatorIndex(**x))
#
# IndicatorIndex.objects.bulk_create(ret)
