def test_create_customer_success(client, auth_headers):
    response = client.post(
        "/customers",
        json={"name": "Test Kunde", "email": "test@example.com", "phone": "123456"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Kunde"
    assert "id" in data


def test_create_customer_without_api_key_fails(client):
    response = client.post(
        "/customers",
        json={"name": "No Key Kunde", "email": None, "phone": None},
    )
    assert response.status_code in (401, 422)  # 422 if header missing entirely


def test_create_customer_with_wrong_api_key_fails(client):
    response = client.post(
        "/customers",
        json={"name": "Wrong Key Kunde", "email": None, "phone": None},
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 401


def test_get_customers_empty_list(client):
    response = client.get("/customers")
    assert response.status_code == 200
    assert response.json() == []


def test_create_job_with_invalid_customer_fails(client, auth_headers):
    response = client.post(
        "/jobs",
        json={"customer_id": 9999, "title": "Ghost Job", "status": "open", "job_date": "2026-08-01"},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_full_profit_calculation_flow(client, auth_headers):
    # 1. Create customer
    customer = client.post(
        "/customers",
        json={"name": "Elektriker Test", "email": None, "phone": None},
        headers=auth_headers,
    ).json()

    # 2. Create job
    job = client.post(
        "/jobs",
        json={
            "customer_id": customer["id"],
            "title": "Test Installation",
            "status": "completed",
            "job_date": "2026-08-01",
        },
        headers=auth_headers,
    ).json()

    # 3. Create material
    material = client.post(
        "/materials",
        json={"name": "Test Kabel", "purchase_price": 10.0},
        headers=auth_headers,
    ).json()

    # 4. Assign material to job (quantity 3 -> cost 30.0)
    client.post(
        "/job_materials",
        json={"job_id": job["id"], "material_id": material["id"], "quantity": 3},
        headers=auth_headers,
    )

    # 5. Create invoice (amount 100.0)
    client.post(
        "/invoices",
        json={"job_id": job["id"], "amount": 100.0, "payment_status": "paid"},
        headers=auth_headers,
    )

    # 6. Check profit calculation: 100.0 - (3 * 10.0) = 70.0
    response = client.get("/jobs/profit")
    assert response.status_code == 200
    results = response.json()
    matching = [r for r in results if r["job_id"] == job["id"]]
    assert len(matching) == 1
    assert matching[0]["invoice_amount"] == 100.0
    assert matching[0]["material_cost"] == 30.0
    assert matching[0]["profit"] == 70.0


def test_delete_job_removes_it(client, auth_headers):
    customer = client.post(
        "/customers",
        json={"name": "To Delete", "email": None, "phone": None},
        headers=auth_headers,
    ).json()

    job = client.post(
        "/jobs",
        json={"customer_id": customer["id"], "title": "Delete Me", "status": "open", "job_date": "2026-08-01"},
        headers=auth_headers,
    ).json()

    delete_response = client.delete(f"/jobs/{job['id']}", headers=auth_headers)
    assert delete_response.status_code == 200

    get_response = client.get("/jobs")
    ids = [j["id"] for j in get_response.json()]
    assert job["id"] not in ids