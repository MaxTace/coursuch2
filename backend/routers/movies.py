from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db import get_db
from models.movie import Movie
from models.category import Category
from schemas.movie import MovieCreate, MovieResponse
from utils.movie_code import generate_movie_code

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("/")
def get_movies(db: Session = Depends(get_db)):
    movies = db.query(Movie).all()
    result = []
    for movie in movies:
        movie_dict = {
            **{c.name: getattr(movie, c.name) for c in movie.__table__.columns},
            "copies_count": len(movie.copies)
        }
        result.append(movie_dict)
    return result


@router.get("/{movie_id}")
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {
        **{c.name: getattr(movie, c.name) for c in movie.__table__.columns},
        "copies_count": len(movie.copies)
    }

@router.post("/change_info/{movie_id}")
def change_movie_info(movie_id: int, movie_update: MovieCreate, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    for key, value in movie_update.model_dump().items():
        setattr(movie, key, value)

    db.commit()
    db.refresh(movie)
    return {
        **{c.name: getattr(movie, c.name) for c in movie.__table__.columns},
        "copies_count": len(movie.copies)
    }


@router.post("/")
def create_movie(movie: MovieCreate, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == movie.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail=f"Category with id {movie.category_id} does not exist")
    
    try:
        movie_code = generate_movie_code(db, movie.category_id)
        new_movie = Movie(**movie.model_dump(), movie_code = movie_code)
        db.add(new_movie)
        db.commit()
        db.refresh(new_movie)
        return {
            **{c.name: getattr(new_movie, c.name) for c in new_movie.__table__.columns},
            "copies_count": len(new_movie.copies)
        }
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating movie: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating movie: {str(e)}")