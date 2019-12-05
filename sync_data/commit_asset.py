import pandas as pd

from sync_data.session import default_engine
from api.models import Fund, Asset, AssetIndustry, StockHolding, BondHolding

conn = default_engine()

windcode = Fund.objects.all().values('windcode')
codes = [x['windcode'] for x in windcode]


def insert_asset():
    data = pd.read_sql("select * from t_ff_asset;", con=conn)
    data = data.drop("id", axis=1)
    data = data[data.windcode.isin(codes)]
    data = data.drop_duplicates()
    data = data.rename(columns={'windcode': 'windcode_id'})
    data = data.to_dict(orient="records")
    asset = [Asset(**x) for x in data]
    Asset.objects.bulk_create(asset)


def insert_industry():
    data = pd.read_sql("select * from t_ff_asset_industry;", con=conn)
    data = data.drop("id", axis=1)
    data = data[data.windcode.isin(codes)]
    data = data.drop_duplicates()
    data = data.rename(columns={'windcode': 'windcode_id'})
    data = data.to_dict(orient="records")
    industry = [AssetIndustry(**x) for x in data]
    AssetIndustry.objects.bulk_create(industry)


def insert_stock():
    data = pd.read_sql("select * from t_ff_asset_stock;", con=conn)
    data = data.drop("id", axis=1)
    data = data[data.windcode.isin(codes)]
    data = data.drop_duplicates()
    data = data.rename(columns={'windcode': 'windcode_id'})
    data = data.to_dict(orient="records")
    stock = [StockHolding(**x) for x in data]
    StockHolding.objects.bulk_create(stock)


def insert_bond():
    data = pd.read_sql("select * from t_ff_asset_bond;", con=conn)
    data = data.drop("id", axis=1)
    data = data[data.windcode.isin(codes)]
    data = data.drop_duplicates()
    data = data.rename(columns={'windcode': 'windcode_id'})
    data = data.to_dict(orient="records")
    bond = [BondHolding(**x) for x in data]
    BondHolding.objects.bulk_create(bond)


if __name__ == '__main__':
    insert_bond()
