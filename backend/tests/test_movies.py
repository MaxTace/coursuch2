import pytest


def make_category(client, name="Боевик", code="ACT"):
    resp = client.post("/categories/", json={"name": name, "code": code})
    return resp.json()


MOVIE_PAYLOAD = {
    "title": "Матрица",
    "director": "Вачовски",
    "actors": "Киану Ривз",
    "country": "США",
    "release_year": 1999,
    "age_rating": 16,
    "description": "Sci-fi боевик",
    "dubbing_languages": "Русский",
    "price": 100,
}


def test_create_movie(client):
    cat = make_category(client)
    payload = {**MOVIE_PAYLOAD, "category_id": cat["id"]}
    resp = client.post("/movies/", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Матрица"
    assert "movie_code" in data
    assert data["movie_code"].startswith("ACT-")


def test_create_movie_invalid_category(client):
    payload = {**MOVIE_PAYLOAD, "category_id": 9999}
    resp = client.post("/movies/", json=payload)
    assert resp.status_code == 400


def test_get_movies(client):
    cat = make_category(client)
    client.post("/movies/", json={**MOVIE_PAYLOAD, "category_id": cat["id"]})
    resp = client.get("/movies/")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_get_movie_by_id(client):
    cat = make_category(client)
    created = client.post("/movies/", json={**MOVIE_PAYLOAD, "category_id": cat["id"]}).json()
    resp = client.get(f"/movies/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Матрица"


def test_get_movie_not_found(client):
    resp = client.get("/movies/9999")
    assert resp.status_code == 404


def test_update_movie(client):
    cat = make_category(client)
    created = client.post("/movies/", json={**MOVIE_PAYLOAD, "category_id": cat["id"]}).json()
    update = {**MOVIE_PAYLOAD, "category_id": cat["id"], "title": "Матрица 2", "price": 150}
    resp = client.post(f"/movies/change_info/{created['id']}", json=update)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Матрица 2"
    assert resp.json()["price"] == 150


def test_movie_code_increments(client):
    cat = make_category(client)
    m1 = client.post("/movies/", json={**MOVIE_PAYLOAD, "category_id": cat["id"]}).json()
    m2 = client.post("/movies/", json={**MOVIE_PAYLOAD, "title": "Матрица 2", "category_id": cat["id"]}).json()
    assert m1["movie_code"] == "ACT-001"
    assert m2["movie_code"] == "ACT-002"
