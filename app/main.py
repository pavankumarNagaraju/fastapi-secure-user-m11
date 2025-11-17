from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from . import models, schemas, crud
from .database import engine, Base, get_db

# Create tables (for simple setups; in production you'd use migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure User API")


@app.get("/")
def read_root():
    return {"message": "Secure User API is running"}


@app.post("/users/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    try:
        user = crud.create_user(db, user_in)
    except IntegrityError:
        # Could be username or email already exists
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists.",
        )
    return user


@app.get("/users/{user_id}", response_model=schemas.UserRead)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return user
