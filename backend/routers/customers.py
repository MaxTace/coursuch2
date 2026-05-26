from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from db import get_db
from models.customer import Customer
from schemas.customer import CustomerCreate

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/")
def get_customers(db: Session = Depends(get_db)):
    return db.query(Customer).all()


@router.post("/")
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):

    new_customer = Customer(**customer.model_dump())

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer