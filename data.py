import sys
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime
from setting import Base
from setting import ENGINE
from setting import session

class Sales(Base):
    """
    ユーザモデル
    """
    __tablename__ = 'each_sales'
    id = Column('id', Integer, primary_key = True)
    store_name = Column('store_name', String(100))
    date = Column('date', String(100))
    item_name = Column('item_name', String(100))
    remain = Column('remain', Integer)
    left = Column('left', Integer)


def main(args):
    """
    メイン関数
    """
    Base.metadata.create_all(bind=ENGINE)

sales = Sales()
sales_a = Sales(store_name = "ウジエスーパー美里店",date = "2022_08_28", item_name = "しそ巻3個入り", remain = 0,left = 15)
sales_b = Sales(store_name = "ウジエスーパー美里店",date = "2022_08_28", item_name = "しそ巻5個入り", remain = 2,left = 10)
sales_c = Sales(store_name = "ウジエスーパー田尻店",date = "2022_08_28", item_name = "しそ巻3個入り", remain = 4,left = 12)
sales_d = Sales(store_name = "ウジエスーパー田尻店",date = "2022_08_28", item_name = "しそ巻5個入り", remain = 5,left = 10)
sales_e = Sales(store_name = "ウジエスーパー美里店",date = "2022_08_29", item_name = "しそ巻3個入り", remain = 7,left = 15)
sales_f = Sales(store_name = "ウジエスーパー美里店",date = "2022_08_29", item_name = "しそ巻5個入り", remain = 1,left = 10)
sales_g = Sales(store_name = "ウジエスーパー田尻店",date = "2022_08_29", item_name = "しそ巻3個入り", remain = 1,left = 15)
sales_h = Sales(store_name = "ウジエスーパー田尻店",date = "2022_08_29", item_name = "しそ巻5個入り", remain = 9,left = 10)
session.add(sales_a)
session.add(sales_b)
session.add(sales_c)
session.add(sales_d)
session.add(sales_e)
session.add(sales_f)
session.add(sales_g)
session.add(sales_h)
session.commit()



if __name__ == "__main__":
    main(sys.argv)