from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db import get_db
from models.category import Category
from schemas.category import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/")
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@router.get("/{category_id}")
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/")
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    try:
        new_category = Category(**category.model_dump())
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return new_category
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Category name or code already exists")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating category: {str(e)}")
