import uuid

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)

    login_sessions: Mapped[List["LoginSession"]] = relationship("LoginSession", back_populates="user", cascade="all, delete-orphan")
    secure_data: Mapped[List["SecureData"]] = relationship("SecureData", back_populates="user", cascade="all, delete-orphan")

class LoginSession(Base):
    __tablename__ = "session"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    token: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    expiry: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="login_sessions")

class SecureData(Base):
    __tablename__ = "encrypted"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    public_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True, default=lambda: uuid.uuid4().hex)
    entry_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    password: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="secure_data")
