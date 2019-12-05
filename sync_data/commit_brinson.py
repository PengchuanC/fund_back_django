import pandas as pd

from sync_data.session import default_engine
from api.models import Fund, Brinson

conn = default_engine()

windcode = Fund.objects.all().values('windcode')
codes = [x['windcode'] for x in windcode]


def insert_brinson():
    data = pd.read_sql("select * from t_ff_brinson;", con=conn)
    data = data.drop("id", axis=1)
    data = data[data.windcode.isin(codes)]
    data = data.drop_duplicates()
    data = data.rename(columns={'windcode': 'windcode_id'})
    data = data.to_dict(orient="records")

    ret = []
    for x in data:
        for k, v in x.items():
            if str(v) == "nan":
                x.update({k: None})
        ret.append(Brinson(**x))

    Brinson.objects.bulk_create(ret)


if __name__ == '__main__':
    insert_brinson()
