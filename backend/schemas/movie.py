from pydantic import BaseModel


class MovieCreate(BaseModel):
    title: str
    director: str
    actors: str
    country: str
    release_year: int
    age_rating: int
    description: str
    dubbing_languages: str
    category_id: int
    price: int


class MovieResponse(MovieCreate):
    id: int
    copies_count: int 

    class Config:
        from_attributes = True