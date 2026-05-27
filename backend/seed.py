import os
import sys
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))

from db import SessionLocal, engine, Base
from models.category import Category
from models.movie import Movie
from models.movie_copy import MovieCopy
from models.customer import Customer
from models.rental import Rental
from utils.movie_code import generate_movie_code
from utils.copie_code import generate_inventory_number


def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def add_copies(db, movie, count, media_type="DVD"):
    existing = db.query(MovieCopy).filter(MovieCopy.movie_id == movie.id).count()
    for i in range(count):
        num = existing + i + 1
        copy = MovieCopy(
            movie_id=movie.id,
            inventory_code=generate_inventory_number(db, movie.id, num),
            media_type=media_type,
            status="available",
        )
        db.add(copy)
    db.flush()


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.query(Category).count() > 0:
            print("Database already seeded, skipping.")
            return

        print("Seeding database...")

        # ── Categories ────────────────────────────────────────────────────────
        cats = {}
        for name, code in [
            ("Боевик", "АКТ"),
            ("Комедия", "КОМ"),
            ("Драма", "ДРМ"),
            ("Фантастика", "ФНТ"),
            ("Триллер", "ТРЛ"),
            ("Ужасы", "УЖС"),
        ]:
            c = Category(name=name, code=code)
            db.add(c)
            cats[name] = c
        db.commit()
        for c in cats.values():
            db.refresh(c)

        # ── Movies ────────────────────────────────────────────────────────────
        def make_movie(title, director, actors, country, year, rating, desc, langs, price, cat_name, copies=2, media="DVD"):
            cat = cats[cat_name]
            code = generate_movie_code(db, cat.id)
            m = Movie(
                title=title, director=director, actors=actors,
                country=country, release_year=year, age_rating=rating,
                description=desc, dubbing_languages=langs,
                price=price, category_id=cat.id, movie_code=code,
            )
            db.add(m)
            db.flush()
            add_copies(db, m, copies, media)
            return m

        matrix = make_movie(
            "Матрица", "Вачовски", "Киану Ривз, Лоренс Фишбёрн, Кэрри-Энн Мосс",
            "США", 1999, 16,
            "Компьютерный хакер узнаёт, что реальность, в которой он живёт, — иллюзия, созданная машинами.",
            "Русский, Английский", 120, "Фантастика", copies=3,
        )
        interstellar = make_movie(
            "Интерстеллар", "Кристофер Нолан", "Мэттью МакКонахи, Энн Хэтэуэй",
            "США", 2014, 0,
            "Группа исследователей отправляется сквозь червоточину в поисках нового дома для человечества.",
            "Русский, Английский", 150, "Фантастика", copies=2,
        )
        die_hard = make_movie(
            "Крепкий орешек", "Джон МакТирнан", "Брюс Уиллис, Алан Рикман",
            "США", 1988, 16,
            "Полицейский Джон МакКлейн в одиночку противостоит террористам, захватившим небоскрёб.",
            "Русский", 100, "Боевик", copies=3,
        )
        terminator = make_movie(
            "Терминатор 2: Судный день", "Джеймс Кэмерон",
            "Арнольд Шварценеггер, Линда Хэмилтон",
            "США", 1991, 16,
            "Терминатор нового поколения прислан уничтожить Джона Коннора. Предыдущий Т-800 должен его защитить.",
            "Русский", 110, "Боевик", copies=2,
        )
        forrest = make_movie(
            "Форрест Гамп", "Роберт Земекис", "Том Хэнкс, Робин Райт",
            "США", 1994, 0,
            "История жизни простого человека из Алабамы, ставшего свидетелем ключевых событий истории США.",
            "Русский", 80, "Драма", copies=3,
        )
        green_mile = make_movie(
            "Зелёная миля", "Фрэнк Дарабонт", "Том Хэнкс, Майкл Кларк Дункан",
            "США", 1999, 12,
            "Надзиратель тюрьмы знакомится с осуждённым, обладающим сверхъестественными способностями.",
            "Русский", 90, "Драма", copies=2,
        )
        home_alone = make_movie(
            "Один дома", "Крис Коламбус", "Маколей Калкин, Джо Пеши",
            "США", 1990, 0,
            "Восьмилетний мальчик остаётся дома один и защищает его от грабителей.",
            "Русский", 70, "Комедия", copies=3,
        )
        silence = make_movie(
            "Молчание ягнят", "Джонатан Демме", "Джоди Фостер, Энтони Хопкинс",
            "США", 1991, 18,
            "Агент ФБР обращается за помощью к заключённому психиатру-каннибалу для поимки маньяка.",
            "Русский", 120, "Триллер", copies=2,
        )
        fight_club = make_movie(
            "Бойцовский клуб", "Дэвид Финчер", "Брэд Питт, Эдвард Нортон",
            "США", 1999, 18,
            "Офисный работник, страдающий бессонницей, создаёт подпольный бойцовский клуб.",
            "Русский", 130, "Триллер", copies=2,
        )
        shining = make_movie(
            "Сияние", "Стэнли Кубрик", "Джек Николсон, Шелли Дюваль",
            "США", 1980, 18,
            "Писатель с семьёй остаётся зимовать в изолированном отеле, где начинается нечто ужасное.",
            "Русский", 110, "Ужасы", copies=2,
        )

        db.commit()

        # ── Customers ─────────────────────────────────────────────────────────
        def make_customer(full_name, birth, phone, email):
            c = Customer(
                full_name=full_name,
                birth_date=date.fromisoformat(birth),
                phone=phone,
                email=email,
                registration_date=now() - timedelta(days=90),
            )
            db.add(c)
            return c

        ivanov  = make_customer("Иванов Иван Иванович",      "1985-03-15", "+79161234567", "ivanov@mail.ru")
        petrova = make_customer("Петрова Мария Сергеевна",   "1992-07-22", "+79267654321", "petrova@mail.ru")
        sidorov = make_customer("Сидоров Алексей Петрович",  "1978-11-10", "+79371112233", "sidorov@mail.ru")
        kozlova = make_customer("Козлова Наталья Дмитриевна","2001-04-30", "+79484445566", "kozlova@mail.ru")
        popov   = make_customer("Попов Артём Иванович",      "2009-08-15", "+79595556677", "popov@mail.ru")

        db.commit()
        for c in [ivanov, petrova, sidorov, kozlova, popov]:
            db.refresh(c)

        # ── Rentals ───────────────────────────────────────────────────────────
        def get_available_copy(db, movie):
            return db.query(MovieCopy).filter(
                MovieCopy.movie_id == movie.id,
                MovieCopy.status == "available",
            ).first()

        def make_rental(customer, movie, rental_days, issue_offset_days=0, returned=False, overdue_extra=0):
            copy = get_available_copy(db, movie)
            if not copy:
                return None

            price_per_day = movie.price
            rental_price = rental_days * price_per_day
            deposit = rental_price * 2
            issue_dt = now() - timedelta(days=issue_offset_days)
            planned_return = issue_dt + timedelta(days=rental_days)

            penalty = 0.0
            actual_return = None

            if returned:
                actual_return = planned_return + timedelta(days=overdue_extra)
                if overdue_extra > 0:
                    penalty = round(overdue_extra * price_per_day * 1.5, 2)
            elif not returned and now() > planned_return:
                pass  # still active but overdue

            total = round(rental_price + deposit + penalty, 2)

            r = Rental(
                customer_id=customer.id,
                inventory_id=copy.id,
                issue_date=issue_dt,
                planned_return_date=planned_return,
                actual_return_date=actual_return,
                rental_days=rental_days,
                rental_price=rental_price,
                deposit=deposit,
                penalty=penalty,
                total_price=total,
            )
            copy.status = "available" if returned else "rented"
            db.add(r)
            db.flush()
            return r

        # Активные аренды
        make_rental(ivanov,  matrix,     rental_days=5, issue_offset_days=2)
        make_rental(kozlova, home_alone, rental_days=3, issue_offset_days=1)
        make_rental(sidorov, interstellar, rental_days=7, issue_offset_days=1)

        # Просроченная (выдана 10 дней назад на 7 дней — просрочка 3 дня)
        make_rental(petrova, fight_club, rental_days=7, issue_offset_days=10)

        # Возвращённые без штрафа
        make_rental(ivanov,  forrest,   rental_days=3, issue_offset_days=10, returned=True)
        make_rental(petrova, die_hard,  rental_days=2, issue_offset_days=15, returned=True)
        make_rental(sidorov, green_mile, rental_days=5, issue_offset_days=20, returned=True)

        # Возвращённая со штрафом (опоздание 2 дня)
        make_rental(kozlova, terminator, rental_days=3, issue_offset_days=10, returned=True, overdue_extra=2)

        db.commit()
        print("Seeding complete.")

    except Exception as e:
        db.rollback()
        print(f"Seed error: {e}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
