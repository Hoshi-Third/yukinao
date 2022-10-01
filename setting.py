from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

# mysqlのDBの設定
DATABASE = 'mysql://%s:%s@%s/%s?charset=utf8' % (
    "user_name",
    "password",
    "host_ip",
    "db_name",
)
ENGINE = create_engine(
    DATABASE,
    encoding = "utf-8",
    echo=True # Trueだと実行のたびにSQLが出力される
)

# Sessionの作成
session = scoped_session(
  # ORM実行時の設定。自動コミットするか、自動反映するなど。
    sessionmaker(
        autocommit = False,
        autoflush = False,
        bind = ENGINE
    )
)

# modelで使用する
Base = declarative_base()
Base.query = session.query_property()