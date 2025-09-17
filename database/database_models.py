import uuid
from typing import Optional
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username_hash: Mapped[str] = mapped_column(String, unique=True, index=True)

    srp_salt: Mapped[str] = mapped_column(String)
    srp_verifier: Mapped[str] = mapped_column(String)
    master_key_salt: Mapped[str] = mapped_column(String)

    new_srp_salt: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    new_srp_verifier: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    new_master_key_salt: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class AuthEphemeral(Base):
    __tablename__ = "auth"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True, default=lambda: uuid.uuid4().hex)
    user_id: Mapped[int] = mapped_column(Integer)

    ephemeral_b: Mapped[str] = mapped_column(String)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    password_change: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)


class LoginSession(Base):
    __tablename__ = "login"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True, default=lambda: uuid.uuid4().hex)
    user_id: Mapped[int] = mapped_column(Integer)

    session_key: Mapped[str] = mapped_column(String)
    request_count: Mapped[int] = mapped_column(Integer)
    last_used: Mapped[datetime] = mapped_column(DateTime)

    maximum_requests: Mapped[int] = mapped_column(Integer, nullable=True)
    expiry_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    password_change: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)


class SecureData(Base):
    __tablename__ = "data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)

    entry_name: Mapped[str] = mapped_column(String)
    entry_data: Mapped[str] = mapped_column(String)

    new_entry_name: Mapped[str] = mapped_column(String, nullable=True)
    new_entry_data: Mapped[str] = mapped_column(String, nullable=True)
