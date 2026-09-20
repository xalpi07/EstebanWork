import helpers


def test_register_new_client():
    client = helpers.start()
    response = client.post(
        "/register",
        json={"username": "lucia", "email": "lucia@mail.com", "password": "1234"},
    )
    assert response.status_code == 201
    assert response.get_json()["token"] is not None
    assert response.get_json()["user"]["role"] == "client"


def test_register_cannot_choose_admin_role():
    client = helpers.start()
    response = client.post(
        "/register",
        json={
            "username": "lucia",
            "email": "lucia@mail.com",
            "password": "1234",
            "role": "admin",
        },
    )
    assert response.status_code == 201
    assert response.get_json()["user"]["role"] == "client"


def test_register_without_password():
    client = helpers.start()
    response = client.post(
        "/register", json={"username": "lucia", "email": "lucia@mail.com"}
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "Bad Request"


def test_register_with_invalid_email():
    client = helpers.start()
    response = client.post(
        "/register",
        json={"username": "lucia", "email": "correo-malo", "password": "1234"},
    )
    assert response.status_code == 400


def test_register_with_repeated_username():
    client = helpers.start()
    response = client.post(
        "/register",
        json={"username": "maria", "email": "otra@mail.com", "password": "1234"},
    )
    assert response.status_code == 409
    assert response.get_json()["error"] == "Username already exists"


def test_register_with_repeated_email():
    client = helpers.start()
    response = client.post(
        "/register",
        json={
            "username": "otra",
            "email": "maria@petshop.com",
            "password": "1234",
        },
    )
    assert response.status_code == 409
    assert response.get_json()["error"] == "Email already exists"


def test_login_with_correct_data():
    client = helpers.start()
    response = client.post(
        "/login", json={"username": "maria", "password": "client123"}
    )
    assert response.status_code == 200
    assert response.get_json()["token"] is not None


def test_login_with_wrong_password():
    client = helpers.start()
    response = client.post(
        "/login", json={"username": "maria", "password": "equivocada"}
    )
    assert response.status_code == 401
    assert response.get_json()["error"] == "Unauthorized"


def test_login_with_user_that_does_not_exist():
    client = helpers.start()
    response = client.post(
        "/login", json={"username": "nadie", "password": "1234"}
    )
    assert response.status_code == 401


def test_login_without_body():
    client = helpers.start()
    response = client.post("/login", json={})
    assert response.status_code == 400


def test_me_with_token():
    client = helpers.start()
    response = client.get("/me", headers=helpers.client_header(client))
    assert response.status_code == 200
    assert response.get_json()["username"] == "maria"


def test_me_without_token():
    client = helpers.start()
    response = client.get("/me")
    assert response.status_code == 401


def test_me_with_invalid_token():
    client = helpers.start()
    response = client.get("/me", headers=helpers.header("token-inventado"))
    assert response.status_code == 401


def test_login_token_has_expiration():
    client = helpers.start()
    token = helpers.login(client, "maria", "client123")
    data = helpers.decode_token(token)
    assert data["exp"] is not None


def test_me_with_expired_token():
    client = helpers.start()
    user = helpers.db_manager.get_user_by_username("maria")
    response = client.get(
        "/me", headers=helpers.header(helpers.expired_token(user.id))
    )
    assert response.status_code == 401
    assert response.get_json()["error"] == "Unauthorized"
