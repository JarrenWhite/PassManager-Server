from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    login_sessions = relationship("LoginSession", back_populates="user", cascade="all, delete-orphan")
    secure_data = relationship("SecureData", back_populates="user", cascade="all, delete-orphan")

class LoginSession(Base):
    __tablename__ = "session"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    token = Column(String, nullable=False, unique=True)
    expiry = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="login_sessions")

    __table_args__ = (
        Index('idx_token', 'token'),
    )

class SecureData(Base):
    __tablename__ = "encrypted"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    entry_name = Column(String)
    website = Column(String)
    username = Column(String)
    password = Column(String)
    notes = Column(String)
    
    user = relationship("User", back_populates="secure_data")
