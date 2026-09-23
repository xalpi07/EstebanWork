import helpers


def test_create_empty_cart():
    client = helpers.start()
    response = client.post("/carts", headers=helpers.client_header(client))
    assert response.status_code == 201
    assert response.get_json()["status"] == "open"
    assert response.get_json()["items"] == []


def test_add_item_to_cart():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client)
    cart_id = helpers.create_cart(client, headers)

    response = helpers.add_item(client, headers, cart_id, product["id"], 3)
    assert response.status_code == 201

    cart = response.get_json()
    assert len(cart["items"]) == 1
    assert cart["items"][0]["quantity"] == 3
    assert cart["total"] == 8500 * 3


def test_add_the_same_product_twice_sums_the_quantity():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client)
    cart_id = helpers.create_cart(client, headers)

    helpers.add_item(client, headers, cart_id, product["id"], 2)
    response = helpers.add_item(client, headers, cart_id, product["id"], 3)

    cart = response.get_json()
    assert len(cart["items"]) == 1
    assert cart["items"][0]["quantity"] == 5


def test_add_item_with_quantity_zero():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client)
    cart_id = helpers.create_cart(client, headers)

    response = helpers.add_item(client, headers, cart_id, product["id"], 0)
    assert response.status_code == 400


def test_add_item_of_a_product_that_does_not_exist():
    client = helpers.start()
    headers = helpers.client_header(client)
    cart_id = helpers.create_cart(client, headers)

    response = helpers.add_item(client, headers, cart_id, 999, 1)
    assert response.status_code == 404


def test_add_item_to_a_cart_that_does_not_exist():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client)

    response = helpers.add_item(client, headers, 999, product["id"], 1)
    assert response.status_code == 404


def test_change_the_quantity_of_an_item():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client)
    cart_id = helpers.create_cart_with_item(client, headers, product["id"], 4)

    response = client.put(
        f"/carts/{cart_id}/items/{product['id']}",
        json={"quantity": 2},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.get_json()["items"][0]["quantity"] == 2


def test_change_the_quantity_of_an_item_that_is_not_in_the_cart():
    client = helpers.start()
    headers = helpers.client_header(client)
    cart_id = helpers.create_cart(client, headers)

    response = client.put(
        f"/carts/{cart_id}/items/999", json={"quantity": 2}, headers=headers
    )
    assert response.status_code == 404


def test_remove_an_item_from_the_cart():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client)
    cart_id = helpers.create_cart_with_item(client, headers, product["id"], 1)

    response = client.delete(
        f"/carts/{cart_id}/items/{product['id']}", headers=headers
    )
    assert response.status_code == 200
    assert response.get_json()["items"] == []


def test_a_client_cannot_see_the_cart_of_another_client():
    client = helpers.start()
    headers = helpers.client_header(client)
    cart_id = helpers.create_cart(client, headers)

    response = client.get(
        f"/carts/{cart_id}", headers=helpers.other_client_header(client)
    )
    assert response.status_code == 403
    assert response.get_json()["error"] == "Forbidden"


def test_the_cart_can_be_retaken_later():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client)
    cart_id = helpers.create_cart_with_item(client, headers, product["id"], 2)

    response = client.get(f"/carts/{cart_id}", headers=headers)
    assert response.status_code == 200
    assert response.get_json()["status"] == "open"
    assert response.get_json()["items"][0]["quantity"] == 2


def test_the_client_only_sees_his_own_carts():
    client = helpers.start()
    helpers.create_cart(client, helpers.client_header(client))
    helpers.create_cart(client, helpers.other_client_header(client))

    response = client.get("/carts", headers=helpers.client_header(client))
    assert len(response.get_json()) == 1

    response = client.get("/carts", headers=helpers.admin_header(client))
    assert len(response.get_json()) == 2


def test_delete_a_cart():
    client = helpers.start()
    headers = helpers.client_header(client)
    cart_id = helpers.create_cart(client, headers)

    response = client.delete(f"/carts/{cart_id}", headers=headers)
    assert response.status_code == 200

    response = client.get(f"/carts/{cart_id}", headers=headers)
    assert response.status_code == 404
