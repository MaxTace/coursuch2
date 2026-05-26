from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from models.movie_copy import MovieCopy

router = APIRouter(
    prefix="/movies",
    tags=["Movie Copies"]
)

@router.get("/{movie_id}/copies")
def get_movie_copies(movie_id: int, db: Session = Depends(get_db)):
    copies = db.query(MovieCopy).filter(MovieCopy.movie_id == movie_id).all()
    return copies


@router.post("/{movie_id}/copies")
def add_movie_copies(
    movie_id: int,
    copies_count: int,
    inventory_code: str,
    db: Session = Depends(get_db)
):

    created_copies = []

    for i in range(copies_count):

        copy = MovieCopy(
            movie_id=movie_id,
            inventory_code=inventory_code,
            status="available",
            media_type="DVD"
        )

        db.add(copy)

        created_copies.append(copy)

    db.commit()

    return {
        "message": f"Добавлено {copies_count} копий"
    }