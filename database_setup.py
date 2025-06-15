import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

DB_FILENAME = os.getenv("VAULT_PATH", "data/vault.db")
DB_URL = f"sqlite:///{DB_FILENAME}"

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

class Session(Base):
    __tablename__ = "session"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    token = Column(String, nullable=False)
    expiry = Column(DateTime, nullable=False)

class PasswordItem(Base):
    __tablename__ = "password"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    encrypted_id = Column(Integer, nullable=False)
    entry_name = Column(String)
    website = Column(String)

class Encrypted(Base):
    __tablename__ = "encrypted"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    notes = Column(String)


def init_db():
    if not os.path.exists(DB_FILENAME):
        print("Database not found. Creating new database...")
        os.makedirs("data", exist_ok=True)
        engine = create_engine(DB_URL)
        Base.metadata.create_all(engine)
        print("Database created.")

if __name__ == "__main__":
    print("Running database_setup.py as __main__.")
    init_db()
