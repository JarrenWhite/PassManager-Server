import uuid

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    login_sessions = relationship("LoginSession", back_populates="user", cascade="all, delete-orphan")
    secure_data = relationship("SecureData", back_populates="user", cascade="all, delete-orphan")

class LoginSession(Base):
    __tablename__ = "session"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    token = Column(String, nullable=False, unique=True, index=True)
    expiry = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="login_sessions")

class SecureData(Base):
    __tablename__ = "encrypted"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    public_id = Column(String, unique=True, nullable=False, index=True, default=lambda: uuid.uuid4().hex)
    entry_name = Column(String)
    website = Column(String)
    username = Column(String)
    password = Column(String)
    notes = Column(String)
    
    user = relationship("User", back_populates="secure_data")
