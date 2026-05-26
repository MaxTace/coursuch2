from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    code: str


class CategoryResponse(CategoryCreate):
    id: int

    class Config:
        from_attributes = True
