from sqlalchemy.orm import Session
from database_setup import User


def register_user(session: Session, username: str, hashed_password: str)  -> User | None:
    existing_user = session.query(User).filter_by(username=username).first()
    if existing_user:
        return None

    new_user = User(username=username, password_hash=hashed_password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user

def get_user(session: Session, username: str):
    return session.query(User).filter_by(username=username).first()
