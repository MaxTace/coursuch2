from pydantic import BaseModel
from datetime import date


class CustomerCreate(BaseModel):
    full_name: str
    birth_date: date
    phone: str
    email: str


class CustomerResponse(CustomerCreate):
    id: int

    class Config:
        from_attributes = True