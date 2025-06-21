import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

def get_db_filename():
    return os.getenv("VAULT_PATH", "data/vault.db")

def get_db_url():
    return f"sqlite:///" + get_db_filename()

def get_engine():
    return create_engine(get_db_url(), pool_pre_ping=True)

def get_session_local():
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())

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
    db_filename = get_db_filename()
    if not os.path.exists(db_filename):
        print("Database not found. Creating new database...")
        os.makedirs(os.path.dirname(db_filename), exist_ok=True)
        engine = get_engine()
        Base.metadata.create_all(engine)
        print("Database created.")

if __name__ == "__main__":
    print("Running database_setup.py as __main__.")
    init_db()
