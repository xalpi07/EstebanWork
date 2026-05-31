import os
from datetime import datetime

from db import DB_Manager
from JWT_Manager import JWT_Manager
from auth import configure_auth, require_auth
from flask import Flask, request, Response, jsonify, g

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask("user-service")
db_manager = DB_Manager()
jwt_manager = JWT_Manager(
    os.path.join(BASE_DIR, "keys", "private.pem"),
    os.path.join(BASE_DIR, "keys", "public.pem"),
    "RS256",
)
configure_auth(jwt_manager, db_manager)


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


@app.route("/liveness")
def liveness():
    return "<p>Hello, World!</p>"


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if data is None or data.get("username") is None or data.get("password") is None:
        return Response(status=400)

    result = db_manager.insert_user(data.get("username"), data.get("password"), "user")
    user_id = result[0]
    user = db_manager.get_user_by_id(user_id)
    token = create_token(user)
    return jsonify(token=token)


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if data is None or data.get("username") is None or data.get("password") is None:
        return Response(status=400)

    result = db_manager.get_user(data.get("username"), data.get("password"))
    if result is None:
        return Response(status=403)

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
    product = db_manager.get_product_by_id(product_id)
    if product is None:
        return Response(status=404)
    return jsonify(product_to_dict(product))


@app.route("/products", methods=["POST"])
@require_auth(["admin"])
def create_product():
    data = request.get_json()
    if data is None:
        return Response(status=400)

    name = data.get("name")
    price = data.get("price")
    entry_date = parse_date(data.get("entry_date"))
    quantity = data.get("quantity")

    if name is None or price is None or entry_date is None or quantity is None:
        return Response(status=400)

    try:
        quantity = int(quantity)
        price = float(price)
    except (TypeError, ValueError):
        return Response(status=400)

    if quantity < 0 or price < 0:
        return Response(status=400)

    result = db_manager.insert_product(name, price, entry_date, quantity)
    product = db_manager.get_product_by_id(result[0])
    return jsonify(product_to_dict(product)), 201


@app.route("/products/<int:product_id>", methods=["PUT"])
@require_auth(["admin"])
def update_product(product_id):
    data = request.get_json()
    if data is None:
        return Response(status=400)

    name = data.get("name")
    price = data.get("price")
    entry_date = parse_date(data.get("entry_date"))
    quantity = data.get("quantity")

    if name is None or price is None or entry_date is None or quantity is None:
        return Response(status=400)

    if db_manager.get_product_by_id(product_id) is None:
        return Response(status=404)

    try:
        quantity = int(quantity)
        price = float(price)
    except (TypeError, ValueError):
        return Response(status=400)

    if quantity < 0 or price < 0:
        return Response(status=400)

    db_manager.update_product(product_id, name, price, entry_date, quantity)
    product = db_manager.get_product_by_id(product_id)
    return jsonify(product_to_dict(product))


@app.route("/products/<int:product_id>", methods=["DELETE"])
@require_auth(["admin"])
def delete_product(product_id):
    if db_manager.get_product_by_id(product_id) is None:
        return Response(status=404)

    db_manager.delete_product(product_id)
    return Response(status=204)


@app.route("/purchase", methods=["POST"])
@require_auth(["user", "admin"])
def purchase():
    data = request.get_json()
    if data is None:
        return Response(status=400)

    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if product_id is None or quantity is None:
        return Response(status=400)

    try:
        product_id = int(product_id)
        quantity = int(quantity)
    except (TypeError, ValueError):
        return Response(status=400)

    if quantity <= 0:
        return Response(status=400)

    invoice_id, result = db_manager.create_purchase(g.current_user[0], product_id, quantity)

    if result == "not_found":
        return Response(status=404)
    if result == "insufficient_stock":
        return Response(status=400)

    return jsonify(
        {
            "invoice_id": invoice_id,
            "total_price": float(result),
        }
    ), 201


@app.route("/invoices", methods=["GET"])
@require_auth(["user", "admin"])
def list_invoices():
    invoices = db_manager.get_invoices_by_user(g.current_user[0])
    return jsonify([invoice_to_dict(invoice) for invoice in invoices])


@app.route("/invoices/<int:user_id>", methods=["GET"])
@require_auth(["admin"])
def list_client_invoices(user_id):
    if db_manager.get_user_by_id(user_id) is None:
        return Response(status=404)

    invoices = db_manager.get_invoices_by_user(user_id)
    return jsonify([invoice_to_dict(invoice) for invoice in invoices])
