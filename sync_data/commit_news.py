import pandas as pd

from sync_data.session import default_engine
from news.models import News


conn = default_engine()
data = pd.read_sql("select * from t_ff_news;", con=conn)
data = data.to_dict(orient="records")
newslist = [News(**d) for d in data if d['abstract'] is not None]

News.objects.bulk_create(newslist)
