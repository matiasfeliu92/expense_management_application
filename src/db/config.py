import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# db_url = os.getenv('DB_URL')

db_user = os.getenv('DB_USER')
print({'DB_USER': db_user})
db_password = os.getenv('DB_PASSWORD')
print({'DB_PASSWORD': db_password})
db_host = os.getenv('DB_HOST')
print({'DB_HOST': db_host})
db_port = os.getenv('DB_PORT')
print({'DB_PORT': db_port})
db_name = os.getenv('DB_NAME')
print({'DB_NAME': db_name})

db_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{int(db_port)}/{db_name}"
print({'DB_URL': db_url})
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()