from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from . import models, schemas
from .auth import hash_password


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    hashed = hash_password(user_in.password)
    db_user = models.User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hashed,
    )
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # We’ll handle this in the route (e.g., raise HTTPException)
        raise
    db.refresh(db_user)
    return db_user
