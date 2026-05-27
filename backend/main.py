from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import Base, engine

from models.category import Category
from models.movie import Movie
from models.movie_copy import MovieCopy
from models.customer import Customer
from models.rental import Rental
from routers import movie_copies, movies, customers, rentals, category


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Video Rental API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(category.router)
app.include_router(movies.router)
app.include_router(customers.router)
app.include_router(rentals.router)
app.include_router(movie_copies.router)


@app.get("/")
def root():
    return {"message": "Video Rental API"}
