from pydantic import BaseModel
from datetime import datetime


class RentalCreate(BaseModel):
    customer_id: int
    movie_copy_id: int
    rental_days: int


class RentalResponse(BaseModel):
    id: int
    rental_price: float
    deposit: float
    total_price: float

    class Config:
        from_attributes = True