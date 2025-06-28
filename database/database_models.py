from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

class LoginSession(Base):
    __tablename__ = "session"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    token = Column(String, nullable=False)
    expiry = Column(DateTime, nullable=False)

class SecuredData(Base):
    __tablename__ = "encrypted"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    entry_name = Column(String)
    website = Column(String)
    username = Column(String)
    password = Column(String)
    notes = Column(String)
