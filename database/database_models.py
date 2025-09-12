from typing import Optional

from sqlalchemy import String, Integer
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
