from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from db import get_db
from schemas.rental import RentalCreate
from services.rental_service import RentalService

router = APIRouter(prefix="/rentals", tags=["Rentals"])


@router.post("/issue")
def issue_movie(
    rental_data: RentalCreate,
    db: Session = Depends(get_db)
):
    return RentalService.create_rental(db, rental_data)