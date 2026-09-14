import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, BASE_DIR)

TEST_DB_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://postgres:fasd89fa7gs98@localhost:5432/petshop_test",
)

os.environ["DATABASE_URL"] = TEST_DB_URL
os.environ["REDIS_DB"] = "15"

from app import app, db_manager, cache_manager

BILLING_ADDRESS = {
    "full_name": "Maria Rodriguez",
    "phone": "88887777",
    "province": "San Jose",
    "canton": "Escazu",
    "district": "San Rafael",
    "exact_address": "200 metros norte de la iglesia",
}

PAYMENT = {
    "method": "sinpe",
    "sinpe_phone": "88887777",
    "sinpe_reference": "SINPE-0001",
}

CHECKOUT_BODY = {
    "billing_address": BILLING_ADDRESS,
    "payment": PAYMENT,
}


def start():
    db_manager.reset_tables()
    cache_manager.flush()
    db_manager.insert_user("admin", "admin@petshop.com", "admin123", "admin")
    db_manager.insert_user("maria", "maria@petshop.com", "client123", "client")
    db_manager.insert_user("carlos", "carlos@petshop.com", "client123", "client")
    return app.test_client()


def header(token):
    return {"Authorization": f"Bearer {token}"}


def login(client, username, password):
    response = client.post(
        "/login", json={"username": username, "password": password}
    )
    return response.get_json()["token"]


def admin_header(client):
    return header(login(client, "admin", "admin123"))


def client_header(client):
    return header(login(client, "maria", "client123"))


def other_client_header(client):
    return header(login(client, "carlos", "client123"))


def create_product(client, name="Croquetas Adulto Perro 2kg", price=8500, stock=10):
    response = client.post(
        "/products",
        json={
            "name": name,
            "description": "Producto de prueba",
            "price": price,
            "stock": stock,
            "category": "Alimento",
        },
        headers=admin_header(client),
    )
    return response.get_json()


def create_cart(client, headers):
    response = client.post("/carts", headers=headers)
    return response.get_json()["id"]


def add_item(client, headers, cart_id, product_id, quantity=1):
    return client.post(
        f"/carts/{cart_id}/items",
        json={"product_id": product_id, "quantity": quantity},
        headers=headers,
    )


def create_cart_with_item(client, headers, product_id, quantity=1):
    cart_id = create_cart(client, headers)
    add_item(client, headers, cart_id, product_id, quantity)
    return cart_id


def sell(client, headers, product_id, quantity=1):
    cart_id = create_cart_with_item(client, headers, product_id, quantity)
    response = client.post(
        f"/carts/{cart_id}/checkout", json=CHECKOUT_BODY, headers=headers
    )
    return response.get_json()


def cache_is_available():
    cache_manager.store_data("prueba:cache", "ok")
    return cache_manager.get_data("prueba:cache") == "ok"
