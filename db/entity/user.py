from sqlalchemy import Column, Integer, String, Boolean
from db.database import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    email = Column(String)
    phone_number = Column(String)
    is_active = Column(Boolean)
