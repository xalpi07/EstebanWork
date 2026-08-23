import os
import json
from datetime import datetime

from db import (
    DB_Manager,
    ProductNotFoundError,
    InsufficientStockError,
    InvalidPurchaseError,
)
from JWT_Manager import JWT_Manager
from cache import CacheManager
from auth import configure_auth, require_auth
from flask import Flask, request, jsonify, g

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PRODUCT_CACHE_TTL = 300

app = Flask("user-service")
db_manager = DB_Manager()
jwt_manager = JWT_Manager(
    os.path.join(BASE_DIR, "keys", "private.pem"),
    os.path.join(BASE_DIR, "keys", "public.pem"),
    "RS256",
)
cache_manager = CacheManager(
    host="host",
    port="port",
    password="password",
)
configure_auth(jwt_manager, db_manager)


def product_cache_key(product_id):
    return f"product:{product_id}"


def product_to_dict(product):
    return {
        "id": product[0],
        "name": product[1],
        "price": float(product[2]),
        "entry_date": product[3].isoformat(),
        "quantity": product[4],
    }


def invoice_to_dict(invoice):
    return {
        "id": invoice[0],
        "user_id": invoice[1],
        "product_id": invoice[2],
        "quantity": invoice[3],
        "total_price": float(invoice[4]),
        "invoice_date": invoice[5].isoformat(),
    }


def create_token(user):
    return jwt_manager.encode({"id": user[0], "role": user[3]})


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def parse_product_payload(data):
    if data is None:
        return None

    name = data.get("name")
    price = data.get("price")
    entry_date = parse_date(data.get("entry_date"))
    quantity = data.get("quantity")

    if name is None or price is None or entry_date is None or quantity is None:
        return None

    try:
        quantity = int(quantity)
        price = float(price)
    except (TypeError, ValueError):
        return None

    if quantity < 0 or price < 0:
        return None

    return {
        "name": name,
        "price": price,
        "entry_date": entry_date,
        "quantity": quantity,
    }


def normalize_purchase_items(data):
    if data is None:
        return None

    if data.get("products") is not None:
        products = data.get("products")
        if not isinstance(products, list):
            return None
        return products

    if data.get("product_id") is not None or data.get("quantity") is not None:
        return [
            {
                "product_id": data.get("product_id"),
                "quantity": data.get("quantity"),
            }
        ]

    return None


@app.route("/liveness")
def liveness():
    return jsonify(message="Hello, World!")


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if data is None or data.get("username") is None or data.get("password") is None:
        return jsonify(error="Bad Request"), 400

    result = db_manager.insert_user(data.get("username"), data.get("password"), "user")
    user_id = result[0]
    user = db_manager.get_user_by_id(user_id)
    token = create_token(user)
    return jsonify(token=token), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if data is None or data.get("username") is None or data.get("password") is None:
        return jsonify(error="Bad Request"), 400

    result = db_manager.get_user(data.get("username"), data.get("password"))
    if result is None:
        return jsonify(error="Unauthorized"), 401

    token = create_token(result)
    return jsonify(token=token)


@app.route("/me")
@require_auth()
def me():
    user = g.current_user
    return jsonify(id=user[0], username=user[1], role=user[3])


@app.route("/products", methods=["GET"])
@require_auth(["admin"])
def list_products():
    products = db_manager.get_all_products()
    return jsonify([product_to_dict(product) for product in products])


@app.route("/products/<int:product_id>", methods=["GET"])
@require_auth(["admin"])
def get_product(product_id):
    key = product_cache_key(product_id)

    key_exists, _ = cache_manager.check_key(key)
    if key_exists:
        cached = cache_manager.get_data(key)
        if cached is not None:
            return jsonify(json.loads(cached))

    product = db_manager.get_product_by_id(product_id)
    if product is None:
        return jsonify(error="Not Found"), 404

    product_dict = product_to_dict(product)
    cache_manager.store_data(key, json.dumps(product_dict), PRODUCT_CACHE_TTL)
    return jsonify(product_dict)


@app.route("/products", methods=["POST"])
@require_auth(["admin"])
def create_product():
    payload = parse_product_payload(request.get_json())
    if payload is None:
        return jsonify(error="Bad Request"), 400

    result = db_manager.insert_product(
        payload["name"],
        payload["price"],
        payload["entry_date"],
        payload["quantity"],
    )
    product = db_manager.get_product_by_id(result[0])
    cache_manager.delete_data(product_cache_key(product[0]))
    return jsonify(product_to_dict(product)), 201


@app.route("/products/<int:product_id>", methods=["PUT"])
@require_auth(["admin"])
def update_product(product_id):
    payload = parse_product_payload(request.get_json())
    if payload is None:
        return jsonify(error="Bad Request"), 400

    if db_manager.get_product_by_id(product_id) is None:
        return jsonify(error="Not Found"), 404

    db_manager.update_product(
        product_id,
        payload["name"],
        payload["price"],
        payload["entry_date"],
        payload["quantity"],
    )
    cache_manager.delete_data(product_cache_key(product_id))
    product = db_manager.get_product_by_id(product_id)
    return jsonify(product_to_dict(product))


@app.route("/products/<int:product_id>", methods=["DELETE"])
@require_auth(["admin"])
def delete_product(product_id):
    if db_manager.get_product_by_id(product_id) is None:
        return jsonify(error="Not Found"), 404

    db_manager.delete_product(product_id)
    cache_manager.delete_data(product_cache_key(product_id))
    return jsonify(message="Deleted"), 200


@app.route("/purchase", methods=["POST"])
@require_auth(["user", "admin"])
def purchase():
    data = request.get_json()
    items = normalize_purchase_items(data)

    if items is None:
        return jsonify(error="Bad Request"), 400

    try:
        result = db_manager.create_purchase(g.current_user[0], items)
        for invoice in result["invoices"]:
            cache_manager.delete_data(product_cache_key(invoice["product_id"]))
        return jsonify(result), 201
    except ProductNotFoundError as e:
        return jsonify(error="Not Found", product_id=e.product_id), 404
    except InsufficientStockError as e:
        return jsonify(
            error="Insufficient stock",
            product_id=e.product_id,
            available=e.available,
            requested=e.requested,
        ), 400
    except InvalidPurchaseError as e:
        return jsonify(error=e.message), 400


@app.route("/invoices", methods=["GET"])
@require_auth(["user", "admin"])
def list_invoices():
    invoices = db_manager.get_invoices_by_user(g.current_user[0])
    return jsonify([invoice_to_dict(invoice) for invoice in invoices])


@app.route("/invoices/<int:user_id>", methods=["GET"])
@require_auth(["admin"])
def list_client_invoices(user_id):
    if db_manager.get_user_by_id(user_id) is None:
        return jsonify(error="Not Found"), 404

    invoices = db_manager.get_invoices_by_user(user_id)
    return jsonify([invoice_to_dict(invoice) for invoice in invoices])
