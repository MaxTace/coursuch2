def make_category(client):
    return client.post("/categories/", json={"name": "Боевик", "code": "ACT"}).json()


def make_movie(client, cat_id):
    return client.post("/movies/", json={
        "title": "Матрица",
        "director": "Вачовски",
        "actors": "Киану Ривз",
        "country": "США",
        "release_year": 1999,
        "age_rating": 16,
        "description": "Sci-fi",
        "dubbing_languages": "Русский",
        "price": 100,
        "category_id": cat_id,
    }).json()


def test_add_and_get_copies(client):
    cat = make_category(client)
    movie = make_movie(client, cat["id"])

    resp = client.post(f"/movies/{movie['id']}/copies?copies_count=3")
    assert resp.status_code == 200
    assert "3" in resp.json()["message"]

    resp = client.get(f"/movies/{movie['id']}/copies")
    assert resp.status_code == 200
    copies = resp.json()
    assert len(copies) == 3
    assert copies[0]["status"] == "available"


def test_add_copies_with_media_type(client):
    cat = make_category(client)
    movie = make_movie(client, cat["id"])

    resp = client.post(f"/movies/{movie['id']}/copies?copies_count=2&media_type=VHS")
    assert resp.status_code == 200

    copies = client.get(f"/movies/{movie['id']}/copies").json()
    assert len(copies) == 2
    assert copies[0]["media_type"] == "VHS"
    assert copies[1]["media_type"] == "VHS"


def test_copy_inventory_code_format(client):
    cat = make_category(client)
    movie = make_movie(client, cat["id"])
    client.post(f"/movies/{movie['id']}/copies?copies_count=2")
    copies = client.get(f"/movies/{movie['id']}/copies").json()
    assert copies[0]["inventory_code"] == "ACT-001-01"
    assert copies[1]["inventory_code"] == "ACT-001-02"
