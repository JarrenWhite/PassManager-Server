import uuid
from typing import Optional, List
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, LargeBinary
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username_hash: Mapped[bytes] = mapped_column(LargeBinary, unique=True, index=True)

    srp_salt: Mapped[bytes] = mapped_column(LargeBinary)
    srp_verifier: Mapped[bytes] = mapped_column(LargeBinary)
    master_key_salt: Mapped[bytes] = mapped_column(LargeBinary)
    password_change: Mapped[bool] = mapped_column(Boolean)

    new_srp_salt: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    new_srp_verifier: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    new_master_key_salt: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)

    auth_ephemerals: Mapped[List["AuthEphemeral"]] = relationship("AuthEphemeral", back_populates="user", cascade="all, delete-orphan")
    login_sessions: Mapped[List["LoginSession"]] = relationship("LoginSession", back_populates="user", cascade="all, delete-orphan")
    secure_data: Mapped[List["SecureData"]] = relationship("SecureData", back_populates="user", cascade="all, delete-orphan")


class AuthEphemeral(Base):
    __tablename__ = "auth"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True, default=lambda: uuid.uuid4().hex)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    eph_private_b: Mapped[bytes] = mapped_column(LargeBinary)
    eph_public_b: Mapped[bytes] = mapped_column(LargeBinary)
    expiry_time: Mapped[datetime] = mapped_column(DateTime)
    password_change: Mapped[bool] = mapped_column(Boolean)

    user: Mapped["User"] = relationship("User", back_populates="auth_ephemerals")


class LoginSession(Base):
    __tablename__ = "login"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True, default=lambda: uuid.uuid4().hex)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    session_key: Mapped[bytes] = mapped_column(LargeBinary, unique=True, index=True)
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

    entry_name: Mapped[bytes] = mapped_column(LargeBinary)
    entry_data: Mapped[bytes] = mapped_column(LargeBinary)

    new_entry_name: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    new_entry_data: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="secure_data")
