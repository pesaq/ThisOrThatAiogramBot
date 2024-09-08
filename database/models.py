from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    voted = Column(String)
    report_block = Column(Boolean)
    admin = Column(Boolean)

class Questions(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    option1 = Column(String)
    option2 = Column(String)
    option1_points = Column(Integer)
    option2_points = Column(Integer)