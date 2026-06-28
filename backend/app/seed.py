from sqlalchemy.orm import Session
from .database import engine, Base, SessionLocal
from .models.category import Category, CategoryType
from .models.user import User # Ensure User model is registered

DEFAULT_CATEGORIES = [
    ("Food", CategoryType.EXPENSE),
    ("Transport", CategoryType.EXPENSE),
    ("Housing", CategoryType.EXPENSE),
    ("Health", CategoryType.EXPENSE),
    ("Entertainment", CategoryType.EXPENSE),
    ("Shopping", CategoryType.EXPENSE),
    ("Education", CategoryType.EXPENSE),
    ("Savings", CategoryType.EXPENSE),
    ("Other", CategoryType.BOTH),
]

def seed_default_categories():
    db = SessionLocal()
    try:
        for name, cat_type in DEFAULT_CATEGORIES:
            # Check if category already exists
            exists = db.query(Category).filter(Category.name == name, Category.user_id == None).first()
            if not exists:
                category = Category(name=name, type=cat_type, user_id=None)
                db.add(category)
        db.commit()
        print("Default categories seeded successfully.")
    except Exception as e:
        print(f"Error seeding categories: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_default_categories()
