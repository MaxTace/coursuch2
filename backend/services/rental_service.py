from datetime import datetime, timedelta, timezone, date

from fastapi import HTTPException

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
            raise HTTPException(400, "Превышен лимит аренды (максимум 5 активных)")

        if rental_data.rental_days > 7:
            raise HTTPException(400, "Максимальный срок аренды — 7 дней")

        movie_copy = db.query(MovieCopy).filter(
            MovieCopy.id == rental_data.movie_copy_id
        ).first()

        if not movie_copy:
            raise HTTPException(404, "Копия фильма не найдена")

        if movie_copy.status != "available":
            raise HTTPException(400, "Данная копия фильма уже выдана")

        movie = movie_copy.movie
        if movie.age_rating and movie.age_rating > 0 and customer.birth_date:
            today = date.today()
            age = today.year - customer.birth_date.year - (
                (today.month, today.day) < (customer.birth_date.month, customer.birth_date.day)
            )
            if age < movie.age_rating:
                raise HTTPException(
                    400,
                    f"Клиент слишком молод для данного фильма (рейтинг {movie.age_rating}+, возраст клиента {age} лет)"
                )

        movie_price = movie_copy.movie.price

        rental_price = rental_data.rental_days * movie_price
        deposit = rental_price * 2
        total_price = rental_price + deposit

        rental = Rental(
            customer_id=rental_data.customer_id,
            inventory_id=rental_data.movie_copy_id,
            rental_days=rental_data.rental_days,
            planned_return_date=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=rental_data.rental_days),
            rental_price=rental_price,
            deposit=deposit,
            total_price=total_price
        )

        movie_copy.status = "rented"

        db.add(rental)
        db.commit()
        db.refresh(rental)

        return rental

    @staticmethod
    def return_rental(db, rental_id):

        rental = db.query(Rental).filter(Rental.id == rental_id).first()

        if not rental:
            raise HTTPException(404, "Аренда не найдена")

        if rental.actual_return_date is not None:
            raise HTTPException(400, "Фильм уже возвращён")

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        rental.actual_return_date = now

        penalty = 0.0
        if now > rental.planned_return_date:
            overdue_days = (now - rental.planned_return_date).days + 1
            daily_price = rental.rental_price / rental.rental_days
            penalty = overdue_days * daily_price * 1.5

        rental.penalty = round(penalty, 2)
        rental.total_price = round(rental.rental_price + rental.deposit + rental.penalty, 2)

        movie_copy = db.query(MovieCopy).filter(
            MovieCopy.id == rental.inventory_id
        ).first()

        if movie_copy:
            movie_copy.status = "available"

        db.commit()
        db.refresh(rental)

        return rental

    @staticmethod
    def get_all_rentals(db):
        rentals = db.query(Rental).all()
        result = []
        for r in rentals:
            copy = db.query(MovieCopy).filter(MovieCopy.id == r.inventory_id).first()
            result.append({
                "id": r.id,
                "customer_id": r.customer_id,
                "customer_name": r.customer.full_name if r.customer else None,
                "movie_copy_id": r.inventory_id,
                "movie_title": copy.movie.title if copy and copy.movie else None,
                "inventory_code": copy.inventory_code if copy else None,
                "issue_date": r.issue_date,
                "planned_return_date": r.planned_return_date,
                "actual_return_date": r.actual_return_date,
                "rental_days": r.rental_days,
                "rental_price": r.rental_price,
                "deposit": r.deposit,
                "penalty": r.penalty,
                "total_price": r.total_price,
                "is_active": r.actual_return_date is None,
            })
        return result
