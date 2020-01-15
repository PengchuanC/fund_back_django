import pandas as pd

# from api.models import Portfolio, PortfolioExpand, PortfolioCore, PortfolioObserve
# from sync_data.insert import insert

from sync_data.session import default_engine

conn = default_engine()

data = pd.read_sql('select * from t_ff_portfolio_observe',  conn)
data = data.rename(columns={'port_id': 'port_id_id'})
data = data.drop('id', axis=1)
data['port_type'] = 1
data = data[data['port_id_id'] <= 5]
print(data)
data.to_sql("t_ff_portfolio_expand", con=conn, if_exists="append", index=False)
