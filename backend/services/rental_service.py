from datetime import datetime
from datetime import timedelta

from fastapi import HTTPException

from models import movie
from models.rental import Rental
from models.customer import Customer
from models.movie_copy import MovieCopy


class RentalService:

    @staticmethod
    def create_rental(db, rental_data):

        customer = db.query(Customer).filter(
            Customer.id == rental_data.customer_id
        ).first()

        if not customer:
            raise HTTPException(404, "Клиент не найден")

        active_rentals = db.query(Rental).filter(
            Rental.customer_id == customer.id,
            Rental.actual_return_date == None
        ).count()

        if active_rentals >= 5:
            raise HTTPException(400, "Превышен лимит аренды")

        movie_copy = db.query(MovieCopy).filter(
            MovieCopy.id == rental_data.movie_copy_id
        ).first()

        if not movie_copy:
            raise HTTPException(404, "Копия фильма не найдена")

        if movie_copy.status != "available":
            raise HTTPException(400, "Фильм уже выдан")

        rental_price = rental_data.rental_days * movie.price

        deposit = rental_price * 2

        total_price = rental_price + deposit

        rental = Rental(
            customer_id=rental_data.customer_id,
            movie_copy_id=rental_data.movie_copy_id,
            rental_days=rental_data.rental_days,
            planned_return_date=datetime.utcnow() + timedelta(days=rental_data.rental_days),
            rental_price=rental_price,
            deposit=deposit,
            total_price=total_price
        )

        movie_copy.status = "rented"

        db.add(rental)
        db.commit()
        db.refresh(rental)

        return rental