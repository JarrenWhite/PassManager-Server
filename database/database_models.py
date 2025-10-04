import uuid
from typing import Optional, List
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username_hash: Mapped[str] = mapped_column(String, unique=True, index=True)

    srp_salt: Mapped[str] = mapped_column(String)
    srp_verifier: Mapped[str] = mapped_column(String)
    master_key_salt: Mapped[str] = mapped_column(String)
    password_changing: Mapped[bool] = mapped_column(Boolean)

    new_srp_salt: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    new_srp_verifier: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    new_master_key_salt: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    login_sessions: Mapped[List["LoginSession"]] = relationship("LoginSession", back_populates="user", cascade="all, delete-orphan")
    secure_data: Mapped[List["SecureData"]] = relationship("SecureData", back_populates="user", cascade="all, delete-orphan")


class AuthEphemeral(Base):
    __tablename__ = "auth"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True, default=lambda: uuid.uuid4().hex)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    ephemeral_salt: Mapped[str] = mapped_column(String)
    ephemeral_b: Mapped[str] = mapped_column(String)
    expiry_time: Mapped[datetime] = mapped_column(DateTime)
    password_change: Mapped[bool] = mapped_column(Boolean)

    user: Mapped["User"] = relationship("User")


class LoginSession(Base):
    __tablename__ = "login"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True, default=lambda: uuid.uuid4().hex)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    session_key: Mapped[str] = mapped_column(String, unique=True, index=True)
    request_count: Mapped[int] = mapped_column(Integer)
    last_used: Mapped[datetime] = mapped_column(DateTime)

    maximum_requests: Mapped[int] = mapped_column(Integer, nullable=True)
    expiry_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    password_change: Mapped[bool] = mapped_column(Boolean)

    user: Mapped["User"] = relationship("User", back_populates="login_sessions")


class SecureData(Base):
    __tablename__ = "data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True, default=lambda: uuid.uuid4().hex)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    entry_name: Mapped[str] = mapped_column(String)
    entry_data: Mapped[str] = mapped_column(String)

    new_entry_name: Mapped[str] = mapped_column(String, nullable=True)
    new_entry_data: Mapped[str] = mapped_column(String, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="secure_data")
