import helpers


def test_checkout_creates_the_invoice_and_lowers_the_stock():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client, price=8500, stock=10)
    cart_id = helpers.create_cart_with_item(client, headers, product["id"], 3)

    response = client.post(
        f"/carts/{cart_id}/checkout", json=helpers.CHECKOUT_BODY, headers=headers
    )
    assert response.status_code == 201

    invoice = response.get_json()
    assert invoice["invoice_number"].startswith("INV-")
    assert invoice["total"] == 8500 * 3
    assert invoice["status"] == "completed"
    assert invoice["items"][0]["quantity"] == 3

    detalle = client.get(f"/products/{product['id']}", headers=headers)
    assert detalle.get_json()["stock"] == 7


def test_checkout_saves_the_address_and_the_payment():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client)
    invoice = helpers.sell(client, headers, product["id"], 1)

    assert invoice["billing_address"]["province"] == "San Jose"
    assert invoice["billing_address"]["full_name"] == "Maria Rodriguez"
    assert invoice["payment"]["method"] == "sinpe"
    assert invoice["payment"]["sinpe_phone"] == "88887777"


def test_checkout_closes_the_cart():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client)
    cart_id = helpers.create_cart_with_item(client, headers, product["id"], 1)

    client.post(
        f"/carts/{cart_id}/checkout", json=helpers.CHECKOUT_BODY, headers=headers
    )

    response = client.get(f"/carts/{cart_id}", headers=headers)
    assert response.get_json()["status"] == "checked_out"


def test_checkout_of_an_empty_cart():
    client = helpers.start()
    headers = helpers.client_header(client)
    cart_id = helpers.create_cart(client, headers)

    response = client.post(
        f"/carts/{cart_id}/checkout", json=helpers.CHECKOUT_BODY, headers=headers
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "Cart is empty"


def test_checkout_without_enough_stock_does_not_change_anything():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client, stock=2)
    cart_id = helpers.create_cart_with_item(client, headers, product["id"], 5)

    response = client.post(
        f"/carts/{cart_id}/checkout", json=helpers.CHECKOUT_BODY, headers=headers
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "Insufficient stock"
    assert response.get_json()["available"] == 2
    assert response.get_json()["requested"] == 5

    detalle = client.get(f"/products/{product['id']}", headers=headers)
    assert detalle.get_json()["stock"] == 2

    cart = client.get(f"/carts/{cart_id}", headers=headers)
    assert cart.get_json()["status"] == "open"


def test_checkout_twice_on_the_same_cart():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client, stock=10)
    cart_id = helpers.create_cart_with_item(client, headers, product["id"], 1)

    client.post(
        f"/carts/{cart_id}/checkout", json=helpers.CHECKOUT_BODY, headers=headers
    )
    response = client.post(
        f"/carts/{cart_id}/checkout", json=helpers.CHECKOUT_BODY, headers=headers
    )
    assert response.status_code == 409
    assert response.get_json()["error"] == "Cart is already checked out"


def test_checkout_without_billing_address():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client)
    cart_id = helpers.create_cart_with_item(client, headers, product["id"], 1)

    response = client.post(
        f"/carts/{cart_id}/checkout",
        json={"payment": helpers.PAYMENT},
        headers=headers,
    )
    assert response.status_code == 400


def test_checkout_with_an_incomplete_address():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client)
    cart_id = helpers.create_cart_with_item(client, headers, product["id"], 1)

    direccion = dict(helpers.BILLING_ADDRESS)
    direccion["province"] = ""

    response = client.post(
        f"/carts/{cart_id}/checkout",
        json={"billing_address": direccion, "payment": helpers.PAYMENT},
        headers=headers,
    )
    assert response.status_code == 400


def test_checkout_with_an_invalid_payment_method():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client)
    cart_id = helpers.create_cart_with_item(client, headers, product["id"], 1)

    response = client.post(
        f"/carts/{cart_id}/checkout",
        json={
            "billing_address": helpers.BILLING_ADDRESS,
            "payment": {"method": "bitcoin"},
        },
        headers=headers,
    )
    assert response.status_code == 400


def test_checkout_with_sinpe_and_without_phone():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client)
    cart_id = helpers.create_cart_with_item(client, headers, product["id"], 1)

    response = client.post(
        f"/carts/{cart_id}/checkout",
        json={
            "billing_address": helpers.BILLING_ADDRESS,
            "payment": {"method": "sinpe"},
        },
        headers=headers,
    )
    assert response.status_code == 400


def test_checkout_of_the_cart_of_another_client():
    client = helpers.start()
    product = helpers.create_product(client)
    cart_id = helpers.create_cart_with_item(
        client, helpers.client_header(client), product["id"], 1
    )

    response = client.post(
        f"/carts/{cart_id}/checkout",
        json=helpers.CHECKOUT_BODY,
        headers=helpers.other_client_header(client),
    )
    assert response.status_code == 403


def test_the_invoice_keeps_the_price_of_the_day_of_the_sale():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client, price=8500, stock=10)
    invoice = helpers.sell(client, headers, product["id"], 2)

    client.put(
        f"/products/{product['id']}",
        json={"name": product["name"], "price": 20000, "stock": 8},
        headers=helpers.admin_header(client),
    )

    response = client.get(f"/invoices/{invoice['invoice_number']}", headers=headers)
    assert response.get_json()["items"][0]["unit_price"] == 8500
    assert response.get_json()["total"] == 17000
