import pandas as pd

from sync_data.session import default_engine
from api.models import Classify, Fund

conn = default_engine()

windcode = Fund.objects.all().values('windcode')
codes = [x['windcode'] for x in windcode]
data = pd.read_sql("select * from t_ff_classify;", con=conn)
data = data[data.windcode.isin(codes)]
data = data.drop_duplicates(["windcode", "branch", "classify", "update_date"])
data = data.to_dict(orient="records")
classify = [Classify(
    windcode_id=x['windcode'], branch=x["branch"], classify=x["classify"], update_date=x['update_date']
) for x in data]

Classify.objects.bulk_create(classify)
