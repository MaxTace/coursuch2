def test_create_category(client):
    resp = client.post("/categories/", json={"name": "Боевик", "code": "ACT"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Боевик"
    assert data["code"] == "ACT"
    assert "id" in data


def test_create_category_duplicate_raises(client):
    client.post("/categories/", json={"name": "Боевик", "code": "ACT"})
    resp = client.post("/categories/", json={"name": "Боевик", "code": "ACT"})
    assert resp.status_code == 400


def test_get_categories(client):
    client.post("/categories/", json={"name": "Комедия", "code": "COM"})
    client.post("/categories/", json={"name": "Драма", "code": "DRM"})
    resp = client.get("/categories/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_category_by_id(client):
    created = client.post("/categories/", json={"name": "Ужасы", "code": "HOR"}).json()
    resp = client.get(f"/categories/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Ужасы"


def test_get_category_not_found(client):
    resp = client.get("/categories/9999")
    assert resp.status_code == 404
