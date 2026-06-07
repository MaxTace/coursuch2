from typing import Literal

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from models.movie_copy import MovieCopy
from utils.copie_code import generate_inventory_number

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
    copies_count: int = Query(..., ge=1),
    media_type: Literal["DVD", "CD", "VHS"] = Query("DVD"),
    db: Session = Depends(get_db)
):

    created_copies = []

    existing_copies = db.query(MovieCopy).filter(
        MovieCopy.movie_id == movie_id
    ).count()

    for i in range(copies_count):

        next_copy_number = existing_copies + i + 1

        inventory_number = generate_inventory_number(
            db,
            movie_id,
            next_copy_number
        )

        copy = MovieCopy(
            movie_id=movie_id,
            inventory_code=inventory_number,
            status="available",
            media_type=media_type
        )

        db.add(copy)

        created_copies.append(copy)

    db.commit()

    return {
        "message": f"Добавлено {copies_count} копий"
    }