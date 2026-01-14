import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Use SQLITE_PATH env or default file in project root
sqlite_path = os.getenv("SQLITE_PATH", os.path.join(os.getcwd(), "data.sqlite3"))
db_url = f"sqlite:///{sqlite_path}"

engine = create_engine(db_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Import v2 infrastructure models to register them on Base before create_all
try:
    import src_v2.infrastructure.models.user  # noqa: F401
except Exception:
    pass

# Create tables
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
