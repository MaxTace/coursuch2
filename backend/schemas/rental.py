from pydantic import BaseModel, ConfigDict
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
    model_config = ConfigDict(from_attributes=True)
