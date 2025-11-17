import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# You will override this with real Postgres URLs in .env and in GitHub Actions
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5433/secure_user_db",
)

engine = create_engine(DATABASE_URL, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
