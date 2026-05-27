from datetime import datetime, timedelta
from unittest.mock import patch


def setup_data(client):
    cat = client.post("/categories/", json={"name": "Боевик", "code": "ACT"}).json()
    movie = client.post("/movies/", json={
        "title": "Матрица",
        "director": "Вачовски",
        "actors": "Киану Ривз",
        "country": "США",
        "release_year": 1999,
        "age_rating": 16,
        "description": "Sci-fi",
        "dubbing_languages": "Русский",
        "price": 100,
        "category_id": cat["id"],
    }).json()
    client.post(f"/movies/{movie['id']}/copies?copies_count=2")
    copies = client.get(f"/movies/{movie['id']}/copies").json()
    customer = client.post("/customers/", json={
        "full_name": "Иванов Иван",
        "birth_date": "1990-01-01",
        "phone": "+79001234567",
        "email": "ivan@example.com",
    }).json()
    return movie, copies, customer


def test_issue_rental(client):
    movie, copies, customer = setup_data(client)
    resp = client.post("/rentals/issue", json={
        "customer_id": customer["id"],
        "movie_copy_id": copies[0]["id"],
        "rental_days": 3,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["rental_price"] == 300.0   # 3 days * 100
    assert data["deposit"] == 600.0        # rental_price * 2
    assert data["total_price"] == 900.0    # 300 + 600


def test_issue_rental_copy_becomes_rented(client):
    movie, copies, customer = setup_data(client)
    client.post("/rentals/issue", json={
        "customer_id": customer["id"],
        "movie_copy_id": copies[0]["id"],
        "rental_days": 3,
    })
    copies_after = client.get(f"/movies/{movie['id']}/copies").json()
    rented = next(c for c in copies_after if c["id"] == copies[0]["id"])
    assert rented["status"] == "rented"


def test_issue_rental_already_rented(client):
    movie, copies, customer = setup_data(client)
    client.post("/rentals/issue", json={
        "customer_id": customer["id"],
        "movie_copy_id": copies[0]["id"],
        "rental_days": 3,
    })
    resp = client.post("/rentals/issue", json={
        "customer_id": customer["id"],
        "movie_copy_id": copies[0]["id"],
        "rental_days": 3,
    })
    assert resp.status_code == 400


def test_issue_rental_customer_not_found(client):
    _, copies, _ = setup_data(client)
    resp = client.post("/rentals/issue", json={
        "customer_id": 9999,
        "movie_copy_id": copies[0]["id"],
        "rental_days": 3,
    })
    assert resp.status_code == 404


def test_issue_rental_copy_not_found(client):
    _, _, customer = setup_data(client)
    resp = client.post("/rentals/issue", json={
        "customer_id": customer["id"],
        "movie_copy_id": 9999,
        "rental_days": 3,
    })
    assert resp.status_code == 404


def test_return_rental_on_time(client):
    _, copies, customer = setup_data(client)
    rental = client.post("/rentals/issue", json={
        "customer_id": customer["id"],
        "movie_copy_id": copies[0]["id"],
        "rental_days": 5,
    }).json()

    resp = client.post(f"/rentals/{rental['id']}/return")
    assert resp.status_code == 200
    data = resp.json()
    assert data["actual_return_date"] is not None
    assert data["penalty"] == 0.0


def test_return_rental_copy_becomes_available(client):
    movie, copies, customer = setup_data(client)
    rental = client.post("/rentals/issue", json={
        "customer_id": customer["id"],
        "movie_copy_id": copies[0]["id"],
        "rental_days": 5,
    }).json()

    client.post(f"/rentals/{rental['id']}/return")
    copies_after = client.get(f"/movies/{movie['id']}/copies").json()
    returned = next(c for c in copies_after if c["id"] == copies[0]["id"])
    assert returned["status"] == "available"


def test_return_already_returned(client):
    _, copies, customer = setup_data(client)
    rental = client.post("/rentals/issue", json={
        "customer_id": customer["id"],
        "movie_copy_id": copies[0]["id"],
        "rental_days": 5,
    }).json()

    client.post(f"/rentals/{rental['id']}/return")
    resp = client.post(f"/rentals/{rental['id']}/return")
    assert resp.status_code == 400


def test_return_not_found(client):
    resp = client.post("/rentals/9999/return")
    assert resp.status_code == 404


def test_get_all_rentals(client):
    movie, copies, customer = setup_data(client)
    client.post("/rentals/issue", json={
        "customer_id": customer["id"],
        "movie_copy_id": copies[0]["id"],
        "rental_days": 3,
    })
    client.post("/rentals/issue", json={
        "customer_id": customer["id"],
        "movie_copy_id": copies[1]["id"],
        "rental_days": 2,
    })
    resp = client.get("/rentals/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_customer_limit_5_rentals(client):
    movie, copies, customer = setup_data(client)

    cat2 = client.post("/categories/", json={"name": "Комедия", "code": "COM"}).json()
    extra_copies = []
    for i in range(3):
        m = client.post("/movies/", json={
            "title": f"Фильм {i}",
            "director": "Реж",
            "actors": "Акт",
            "country": "RU",
            "release_year": 2000,
            "age_rating": 0,
            "description": "desc",
            "dubbing_languages": "ru",
            "price": 50,
            "category_id": cat2["id"],
        }).json()
        client.post(f"/movies/{m['id']}/copies?copies_count=1")
        c = client.get(f"/movies/{m['id']}/copies").json()[0]
        extra_copies.append(c)

    for c in [copies[0], copies[1], extra_copies[0], extra_copies[1], extra_copies[2]]:
        client.post("/rentals/issue", json={
            "customer_id": customer["id"],
            "movie_copy_id": c["id"],
            "rental_days": 1,
        })

    cat3 = client.post("/categories/", json={"name": "Триллер", "code": "THR"}).json()
    m6 = client.post("/movies/", json={
        "title": "Шестой",
        "director": "Реж",
        "actors": "Акт",
        "country": "RU",
        "release_year": 2000,
        "age_rating": 0,
        "description": "desc",
        "dubbing_languages": "ru",
        "price": 50,
        "category_id": cat3["id"],
    }).json()
    client.post(f"/movies/{m6['id']}/copies?copies_count=1")
    c6 = client.get(f"/movies/{m6['id']}/copies").json()[0]

    resp = client.post("/rentals/issue", json={
        "customer_id": customer["id"],
        "movie_copy_id": c6["id"],
        "rental_days": 1,
    })
    assert resp.status_code == 400


def test_age_restriction_blocks_underage_customer(client):
    cat = client.post("/categories/", json={"name": "Ужасы", "code": "HOR"}).json()
    movie = client.post("/movies/", json={
        "title": "Фильм 18+",
        "director": "Реж",
        "actors": "Акт",
        "country": "США",
        "release_year": 2020,
        "age_rating": 18,
        "description": "Страшно",
        "dubbing_languages": "Русский",
        "price": 150,
        "category_id": cat["id"],
    }).json()
    client.post(f"/movies/{movie['id']}/copies?copies_count=1")
    copies = client.get(f"/movies/{movie['id']}/copies").json()

    young_customer = client.post("/customers/", json={
        "full_name": "Молодой Юнец",
        "birth_date": "2015-06-15",
        "phone": "+79009999999",
        "email": "young@example.com",
    }).json()

    resp = client.post("/rentals/issue", json={
        "customer_id": young_customer["id"],
        "movie_copy_id": copies[0]["id"],
        "rental_days": 2,
    })
    assert resp.status_code == 400
    assert "молод" in resp.json()["detail"].lower()


def test_age_restriction_allows_adult_customer(client):
    cat = client.post("/categories/", json={"name": "Триллер18", "code": "T18"}).json()
    movie = client.post("/movies/", json={
        "title": "Взрослый фильм",
        "director": "Реж",
        "actors": "Акт",
        "country": "США",
        "release_year": 2020,
        "age_rating": 18,
        "description": "Для взрослых",
        "dubbing_languages": "Русский",
        "price": 200,
        "category_id": cat["id"],
    }).json()
    client.post(f"/movies/{movie['id']}/copies?copies_count=1")
    copies = client.get(f"/movies/{movie['id']}/copies").json()

    adult_customer = client.post("/customers/", json={
        "full_name": "Взрослый Иван",
        "birth_date": "1990-01-01",
        "phone": "+79008888888",
        "email": "adult@example.com",
    }).json()

    resp = client.post("/rentals/issue", json={
        "customer_id": adult_customer["id"],
        "movie_copy_id": copies[0]["id"],
        "rental_days": 2,
    })
    assert resp.status_code == 200


def test_max_7_days_enforced(client):
    movie, copies, customer = setup_data(client)
    resp = client.post("/rentals/issue", json={
        "customer_id": customer["id"],
        "movie_copy_id": copies[0]["id"],
        "rental_days": 8,
    })
    assert resp.status_code == 400
    assert "7" in resp.json()["detail"]
