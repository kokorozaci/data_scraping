"""
2)Сложить все новости в БД
"""
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, BigInteger, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from task_1_parse_news import NewsScraper as ns

engine = create_engine('sqlite:///news.db', echo=True)
Base = declarative_base()

class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    source = Column(String(255))
    name = Column(String)
    link = Column(String)
    date = Column(DateTime(timezone=True))

    def __init__(self, source, name, link, date):
        self.source = source
        self.name = name
        self.link = link
        self.date = date


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

session = Session()

news = ns()
for new in news.news:
    session.add(News(new['source'], new['name'], new['link'], new['date']))

session.commit()
session.close()
