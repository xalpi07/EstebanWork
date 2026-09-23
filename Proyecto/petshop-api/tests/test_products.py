import helpers


def test_list_products_when_there_are_none():
    client = helpers.start()
    response = client.get("/products", headers=helpers.client_header(client))
    assert response.status_code == 200
    assert response.get_json() == []


def test_list_products_without_token():
    client = helpers.start()
    response = client.get("/products")
    assert response.status_code == 401


def test_create_product_as_admin():
    client = helpers.start()
    response = client.post(
        "/products",
        json={
            "name": "Arena Sanitaria Gato 10L",
            "description": "Arena aglomerante",
            "price": 5400,
            "stock": 18,
            "category": "Higiene",
        },
        headers=helpers.admin_header(client),
    )
    assert response.status_code == 201
    assert response.get_json()["name"] == "Arena Sanitaria Gato 10L"
    assert response.get_json()["stock"] == 18


def test_create_product_as_client_is_forbidden():
    client = helpers.start()
    response = client.post(
        "/products",
        json={"name": "Juguete", "price": 2900, "stock": 5},
        headers=helpers.client_header(client),
    )
    assert response.status_code == 403
    assert response.get_json()["error"] == "Forbidden"


def test_create_product_without_name():
    client = helpers.start()
    response = client.post(
        "/products",
        json={"price": 2900, "stock": 5},
        headers=helpers.admin_header(client),
    )
    assert response.status_code == 400


def test_create_product_with_negative_price():
    client = helpers.start()
    response = client.post(
        "/products",
        json={"name": "Juguete", "price": -100, "stock": 5},
        headers=helpers.admin_header(client),
    )
    assert response.status_code == 400


def test_create_product_with_negative_stock():
    client = helpers.start()
    response = client.post(
        "/products",
        json={"name": "Juguete", "price": 2900, "stock": -3},
        headers=helpers.admin_header(client),
    )
    assert response.status_code == 400


def test_get_product_by_id():
    client = helpers.start()
    product = helpers.create_product(client)
    response = client.get(
        f"/products/{product['id']}", headers=helpers.client_header(client)
    )
    assert response.status_code == 200
    assert response.get_json()["id"] == product["id"]


def test_get_product_that_does_not_exist():
    client = helpers.start()
    response = client.get("/products/999", headers=helpers.client_header(client))
    assert response.status_code == 404
    assert response.get_json()["error"] == "Not Found"


def test_update_product_as_admin():
    client = helpers.start()
    product = helpers.create_product(client)
    response = client.put(
        f"/products/{product['id']}",
        json={
            "name": "Croquetas Adulto Perro 4kg",
            "price": 12000,
            "stock": 7,
            "category": "Alimento",
        },
        headers=helpers.admin_header(client),
    )
    assert response.status_code == 200
    assert response.get_json()["price"] == 12000
    assert response.get_json()["stock"] == 7


def test_update_product_that_does_not_exist():
    client = helpers.start()
    response = client.put(
        "/products/999",
        json={"name": "Algo", "price": 100, "stock": 1},
        headers=helpers.admin_header(client),
    )
    assert response.status_code == 404


def test_update_product_as_client_is_forbidden():
    client = helpers.start()
    product = helpers.create_product(client)
    response = client.put(
        f"/products/{product['id']}",
        json={"name": "Algo", "price": 100, "stock": 1},
        headers=helpers.client_header(client),
    )
    assert response.status_code == 403


def test_delete_product_hides_it_from_the_client():
    client = helpers.start()
    product = helpers.create_product(client)

    response = client.delete(
        f"/products/{product['id']}", headers=helpers.admin_header(client)
    )
    assert response.status_code == 200

    listado = client.get("/products", headers=helpers.client_header(client))
    assert listado.get_json() == []

    detalle = client.get(
        f"/products/{product['id']}", headers=helpers.client_header(client)
    )
    assert detalle.status_code == 404


def test_delete_product_as_client_is_forbidden():
    client = helpers.start()
    product = helpers.create_product(client)
    response = client.delete(
        f"/products/{product['id']}", headers=helpers.client_header(client)
    )
    assert response.status_code == 403


def test_delete_product_that_does_not_exist():
    client = helpers.start()
    response = client.delete("/products/999", headers=helpers.admin_header(client))
    assert response.status_code == 404
