import helpers


def test_the_product_list_is_saved_in_the_cache():
    client = helpers.start()
    if not helpers.cache_is_available():
        return

    helpers.create_product(client)
    client.get("/products", headers=helpers.client_header(client))

    existe, ttl = helpers.cache_manager.check_key("products:all")
    assert existe == True
    assert ttl > 0
    assert ttl <= 300


def test_the_product_detail_is_saved_with_ttl():
    client = helpers.start()
    if not helpers.cache_is_available():
        return

    product = helpers.create_product(client)
    client.get(f"/products/{product['id']}", headers=helpers.client_header(client))

    existe, ttl = helpers.cache_manager.check_key(f"product:{product['id']}")
    assert existe == True
    assert ttl > 0


def test_updating_a_product_erases_the_cache():
    client = helpers.start()
    if not helpers.cache_is_available():
        return

    product = helpers.create_product(client)
    client.get("/products", headers=helpers.client_header(client))

    client.put(
        f"/products/{product['id']}",
        json={"name": product["name"], "price": 9999, "stock": 5},
        headers=helpers.admin_header(client),
    )

    existe, ttl = helpers.cache_manager.check_key("products:all")
    assert existe == False


def test_the_cache_does_not_return_an_old_stock_after_a_sale():
    client = helpers.start()
    if not helpers.cache_is_available():
        return

    headers = helpers.client_header(client)
    product = helpers.create_product(client, stock=10)

    response = client.get(f"/products/{product['id']}", headers=headers)
    assert response.get_json()["stock"] == 10

    helpers.sell(client, headers, product["id"], 4)

    response = client.get(f"/products/{product['id']}", headers=headers)
    assert response.get_json()["stock"] == 6


def test_the_invoice_is_saved_in_the_cache():
    client = helpers.start()
    if not helpers.cache_is_available():
        return

    headers = helpers.client_header(client)
    product = helpers.create_product(client)
    invoice = helpers.sell(client, headers, product["id"], 1)

    client.get(f"/invoices/{invoice['invoice_number']}", headers=headers)

    existe, ttl = helpers.cache_manager.check_key(
        f"invoice:{invoice['invoice_number']}"
    )
    assert existe == True
    assert ttl <= 600


def test_the_refund_erases_the_cache_of_the_invoice():
    client = helpers.start()
    if not helpers.cache_is_available():
        return

    headers = helpers.client_header(client)
    product = helpers.create_product(client)
    invoice = helpers.sell(client, headers, product["id"], 1)

    client.get(f"/invoices/{invoice['invoice_number']}", headers=headers)
    client.post(
        f"/invoices/{invoice['invoice_number']}/refund",
        headers=helpers.admin_header(client),
    )

    response = client.get(f"/invoices/{invoice['invoice_number']}", headers=headers)
    assert response.get_json()["status"] == "refunded"
