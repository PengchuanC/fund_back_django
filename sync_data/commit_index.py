import pandas as pd

from sync_data.session import default_engine
from api.models import Index, IndexClosePrice

conn = default_engine()


def insert_index():
    data = pd.read_sql("select * from t_ff_index;", con=conn)
    data = data.drop("id", axis=1)
    data = data.drop_duplicates()
    data = data.rename(columns={'windcode': 'windcode'})
    data = data.to_dict(orient="records")

    ret = []
    for x in data:
        for k, v in x.items():
            if str(v) == "nan":
                x.update({k: None})
        ret.append(Index(**x))

    Index.objects.bulk_create(ret)


def insert_cp():
    data = pd.read_sql("select * from t_ff_index_cp;", con=conn)
    data = data.drop("id", axis=1)
    data = data.drop_duplicates()
    data = data.rename(columns={'windcode': 'windcode_id'})
    data = data.to_dict(orient="records")

    ret = []
    for x in data:
        for k, v in x.items():
            if str(v) == "nan":
                x.update({k: None})
        ret.append(IndexClosePrice(**x))

    IndexClosePrice.objects.bulk_create(ret)


if __name__ == '__main__':
    insert_index()
    insert_cp()
