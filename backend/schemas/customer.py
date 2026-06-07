from pydantic import BaseModel, ConfigDict
from datetime import date


class CustomerCreate(BaseModel):
    full_name: str
    birth_date: date
    phone: str
    email: str


class CustomerResponse(CustomerCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)
