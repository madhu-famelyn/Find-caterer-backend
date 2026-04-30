import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in environment variables")

# ✅ FIX: Prevent SSL connection drop / stale connection reuse
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,    # ⭐ checks connection before using
    pool_recycle=1800,     # ♻️ recycle connections every 30 mins
    echo=False             # set True only for SQL debugging
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# ✅ Safe DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
