import os

import uvicorn

from src.db.config import Base, engine, SessionLocal
from src.models import Category

DEFAULT_CATEGORIES = [
    ("salary", "This category covers the collection of salaries for jobs"),
    ("service payment", "This category covers the payment of utility bills such as electricity, gas, telephone, internet, water, etc."),
    ("shopping", "This category covers purchases made, whether food, clothing, appliances, household items, furniture, etc."),
    ("rent", "This category covers the payment of rent for housing, whether apartments or houses."),
    ("expense", "This category covers the payment of real estate expenses in the buildings/houses where one lives."),
]


def seed_categories():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Category).count() == 0:
            db.add_all([Category(name=name, description=description) for name, description in DEFAULT_CATEGORIES])
            db.commit()
            print("Seeded default categories")
        else:
            print("Categories already present, skipping seed")
    finally:
        db.close()


def main():
    seed_categories()
    reload_app = os.getenv("APP_RELOAD", "").lower() in ("1", "true", "yes")
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=reload_app,
    )


if __name__ == "__main__":
    main()
