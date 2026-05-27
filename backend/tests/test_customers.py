CUSTOMER_PAYLOAD = {
    "full_name": "Иванов Иван Иванович",
    "birth_date": "1990-01-15",
    "phone": "+79001234567",
    "email": "ivan@example.com",
}


def test_create_customer(client):
    resp = client.post("/customers/", json=CUSTOMER_PAYLOAD)
    assert resp.status_code == 200
    data = resp.json()
    assert data["full_name"] == "Иванов Иван Иванович"
    assert data["email"] == "ivan@example.com"
    assert "id" in data


def test_get_customers(client):
    client.post("/customers/", json=CUSTOMER_PAYLOAD)
    client.post("/customers/", json={**CUSTOMER_PAYLOAD, "email": "other@example.com"})
    resp = client.get("/customers/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_customers_empty(client):
    resp = client.get("/customers/")
    assert resp.status_code == 200
    assert resp.json() == []
