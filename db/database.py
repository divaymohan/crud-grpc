from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

DATABASE_URL = "mysql+mysqlconnector://root:password@localhost:3306/proto_demo"
engine = create_engine(DATABASE_URL, echo=True)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)