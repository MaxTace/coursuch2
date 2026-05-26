from fastapi import FastAPI

from db import Base, engine

from models.category import Category
from models.movie import Movie
from models.movie_copy import MovieCopy
from models.customer import Customer
from models.rental import Rental
from routers import movie_copies, movies, customers, rentals, category



Base.metadata.create_all(bind=engine)

app = FastAPI(title="Video Rental API")


app.include_router(category.router)
app.include_router(movies.router)
app.include_router(customers.router)
app.include_router(rentals.router)
app.include_router(movie_copies.router)


@app.get("/")
def root():
    return {"message": "Video Rental API"}