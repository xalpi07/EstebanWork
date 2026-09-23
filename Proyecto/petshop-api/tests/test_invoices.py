import helpers


def test_the_client_sees_his_own_invoices():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client, stock=20)
    helpers.sell(client, headers, product["id"], 1)
    helpers.sell(client, helpers.other_client_header(client), product["id"], 1)

    response = client.get("/invoices", headers=headers)
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_the_admin_sees_all_the_invoices():
    client = helpers.start()
    product = helpers.create_product(client, stock=20)
    helpers.sell(client, helpers.client_header(client), product["id"], 1)
    helpers.sell(client, helpers.other_client_header(client), product["id"], 1)

    response = client.get("/invoices", headers=helpers.admin_header(client))
    assert len(response.get_json()) == 2


def test_search_an_invoice_by_its_number():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client)
    invoice = helpers.sell(client, headers, product["id"], 1)

    response = client.get(f"/invoices/{invoice['invoice_number']}", headers=headers)
    assert response.status_code == 200
    assert response.get_json()["invoice_number"] == invoice["invoice_number"]


def test_search_an_invoice_that_does_not_exist():
    client = helpers.start()
    response = client.get(
        "/invoices/INV-2026-999999", headers=helpers.client_header(client)
    )
    assert response.status_code == 404


def test_a_client_cannot_see_the_invoice_of_another_client():
    client = helpers.start()
    product = helpers.create_product(client)
    invoice = helpers.sell(client, helpers.client_header(client), product["id"], 1)

    response = client.get(
        f"/invoices/{invoice['invoice_number']}",
        headers=helpers.other_client_header(client),
    )
    assert response.status_code == 403


def test_the_refund_returns_the_stock():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client, stock=10)
    invoice = helpers.sell(client, headers, product["id"], 4)

    detalle = client.get(f"/products/{product['id']}", headers=headers)
    assert detalle.get_json()["stock"] == 6

    response = client.post(
        f"/invoices/{invoice['invoice_number']}/refund",
        headers=helpers.admin_header(client),
    )
    assert response.status_code == 200
    assert response.get_json()["status"] == "refunded"

    detalle = client.get(f"/products/{product['id']}", headers=headers)
    assert detalle.get_json()["stock"] == 10


def test_the_same_invoice_cannot_be_refunded_twice():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client)
    invoice = helpers.sell(client, headers, product["id"], 1)

    client.post(
        f"/invoices/{invoice['invoice_number']}/refund",
        headers=helpers.admin_header(client),
    )
    response = client.post(
        f"/invoices/{invoice['invoice_number']}/refund",
        headers=helpers.admin_header(client),
    )
    assert response.status_code == 409
    assert response.get_json()["error"] == "Invoice was already refunded"


def test_a_client_cannot_refund():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client)
    invoice = helpers.sell(client, headers, product["id"], 1)

    response = client.post(
        f"/invoices/{invoice['invoice_number']}/refund", headers=headers
    )
    assert response.status_code == 403


def test_refund_an_invoice_that_does_not_exist():
    client = helpers.start()
    response = client.post(
        "/invoices/INV-2026-999999/refund", headers=helpers.admin_header(client)
    )
    assert response.status_code == 404


def test_the_admin_corrects_the_sinpe_reference():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client)
    invoice = helpers.sell(client, headers, product["id"], 1)

    response = client.put(
        f"/invoices/{invoice['invoice_number']}",
        json={"sinpe_reference": "SINPE-CORREGIDO"},
        headers=helpers.admin_header(client),
    )
    assert response.status_code == 200
    assert response.get_json()["payment"]["sinpe_reference"] == "SINPE-CORREGIDO"


def test_only_a_refunded_invoice_can_be_deleted():
    client = helpers.start()
    headers = helpers.client_header(client)
    product = helpers.create_product(client)
    invoice = helpers.sell(client, headers, product["id"], 1)
    admin = helpers.admin_header(client)

    response = client.delete(f"/invoices/{invoice['invoice_number']}", headers=admin)
    assert response.status_code == 409

    client.post(f"/invoices/{invoice['invoice_number']}/refund", headers=admin)

    response = client.delete(f"/invoices/{invoice['invoice_number']}", headers=admin)
    assert response.status_code == 200

    response = client.get(f"/invoices/{invoice['invoice_number']}", headers=admin)
    assert response.status_code == 404
