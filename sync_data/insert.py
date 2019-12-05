import pandas as pd

from sync_data.session import default_engine
from api.models import Fund

conn = default_engine()


def insert(model, name):
    windcode = Fund.objects.all().values('windcode')
    codes = [x['windcode'] for x in windcode]
    data = pd.read_sql(f"select * from {name};", con=conn)
    try:
        data = data.drop("id", axis=1)
    except KeyError:
        pass
    try:
        data = data[data.windcode.isin(codes)]
        data = data.rename(columns={'windcode': 'windcode_id'})
    except AttributeError:
        pass
    data = data.drop_duplicates()
    data = data.to_dict(orient="records")

    ret = []
    for x in data:
        for k, v in x.items():
            if str(v) == "nan":
                x.update({k: None})
        ret.append(model(**x))

    model.objects.bulk_create(ret)


def insert_port(model, name):
    data = pd.read_sql(f"select * from {name};", con=conn)
    try:
        data = data.drop("id", axis=1)
    except KeyError:
        pass
    data = data.rename(columns={"port_id": "port_id_id"})
    data = data.drop_duplicates()
    data = data.to_dict(orient="records")

    ret = []
    for x in data:
        for k, v in x.items():
            if str(v) == "nan":
                x.update({k: None})
        ret.append(model(**x))

    model.objects.bulk_create(ret)


if __name__ == '__main__':
    from api.models import FundPerformance, Portfolio, PortfolioCore, PortfolioObserve, Style, Index, IndexClosePrice
    # insert(FundPerformance, "t_ff_performance")
    # insert(Portfolio, "t_ff_portfolio")
    # insert_port(PortfolioCore, "t_ff_portfolio_core")
    # insert_port(PortfolioObserve, "t_ff_portfolio_observe")
    # insert(Style, "t_ff_style")
    # insert(Index, 't_ff_index')
    insert(IndexClosePrice, 't_ff_index_cp')