import helpers


def test_a_client_cannot_list_users():
    client = helpers.start()
    response = client.get("/users", headers=helpers.client_header(client))
    assert response.status_code == 403


def test_a_client_cannot_create_users():
    client = helpers.start()
    response = client.post(
        "/users",
        json={"username": "nuevo", "email": "nuevo@mail.com", "password": "1234"},
        headers=helpers.client_header(client),
    )
    assert response.status_code == 403


def test_a_client_cannot_delete_users():
    client = helpers.start()
    response = client.delete("/users/2", headers=helpers.client_header(client))
    assert response.status_code == 403


def test_the_admin_lists_the_users():
    client = helpers.start()
    response = client.get("/users", headers=helpers.admin_header(client))
    assert response.status_code == 200
    assert len(response.get_json()) == 3


def test_the_admin_creates_another_admin():
    client = helpers.start()
    response = client.post(
        "/users",
        json={
            "username": "admin2",
            "email": "admin2@petshop.com",
            "password": "1234",
            "role": "admin",
        },
        headers=helpers.admin_header(client),
    )
    assert response.status_code == 201
    assert response.get_json()["role"] == "admin"


def test_the_admin_changes_the_role_of_a_user():
    client = helpers.start()
    response = client.put(
        "/users/2", json={"role": "admin"}, headers=helpers.admin_header(client)
    )
    assert response.status_code == 200
    assert response.get_json()["role"] == "admin"


def test_the_admin_cannot_delete_himself():
    client = helpers.start()
    response = client.delete("/users/1", headers=helpers.admin_header(client))
    assert response.status_code == 400


def test_a_deactivated_user_cannot_use_his_token():
    client = helpers.start()
    token = helpers.login(client, "maria", "client123")

    client.delete("/users/2", headers=helpers.admin_header(client))

    response = client.get("/me", headers=helpers.header(token))
    assert response.status_code == 401


def test_a_deactivated_user_cannot_log_in_again():
    client = helpers.start()
    client.delete("/users/2", headers=helpers.admin_header(client))

    response = client.post(
        "/login", json={"username": "maria", "password": "client123"}
    )
    assert response.status_code == 401


def test_all_the_protected_endpoints_ask_for_a_token():
    client = helpers.start()
    rutas = ["/me", "/users", "/products", "/products/1", "/carts", "/invoices"]

    for ruta in rutas:
        response = client.get(ruta)
        assert response.status_code == 401
