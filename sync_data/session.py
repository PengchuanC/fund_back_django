from sqlalchemy import create_engine
from sync_data.config import DATABASES


def make_engine(database):
    uri = f"mysql+pymysql://{database['USER']}:{database['PASSWORD']}@" \
          f"{database['HOST']}:{database['PORT']}/{database['NAME']}?charset=utf8mb4"
    engine = create_engine(uri)
    return engine


def default_engine():
    return make_engine(DATABASES["default"])
