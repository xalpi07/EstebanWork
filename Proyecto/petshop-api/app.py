import os
import json
from datetime import datetime, timedelta, timezone

from db import (
    DB_Manager,
    ProductNotFoundError,
    InsufficientStockError,
    CartNotFoundError,
    CartClosedError,
    InvalidPurchaseError,
    InvoiceNotFoundError,
    InvoiceAlreadyRefundedError,
)
from JWT_Manager import JWT_Manager
from cache import CacheManager
from auth import configure_auth, require_auth
from flask import Flask, request, jsonify, g

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PRODUCT_CACHE_TTL = 300
INVOICE_CACHE_TTL = 600
TOKEN_TTL_HOURS = 8

app = Flask("petshop-api")
db_manager = DB_Manager()
jwt_manager = JWT_Manager(
    os.path.join(BASE_DIR, "keys", "private.pem"),
    os.path.join(BASE_DIR, "keys", "public.pem"),
    "RS256",
)
cache_manager = CacheManager(
    host=os.getenv("REDIS_HOST", "127.0.0.1"),
    port=int(os.getenv("REDIS_PORT", 16379)),
    password=os.getenv("REDIS_PASSWORD") or None,
    db=int(os.getenv("REDIS_DB", 0)),
)
configure_auth(jwt_manager, db_manager)


def product_cache_key(product_id):
    return f"product:{product_id}"


def products_cache_key():
    return "products:all"


def invoice_cache_key(invoice_number):
    return f"invoice:{invoice_number}"


def invalidate_product_cache(product_id):
    cache_manager.delete_data(product_cache_key(product_id))
    cache_manager.delete_data(products_cache_key())


def invalidate_invoice_cache(invoice_number):
    cache_manager.delete_data(invoice_cache_key(invoice_number))


def user_to_dict(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
    }


def product_to_dict(product):
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": float(product.price),
        "stock": product.stock,
        "category": product.category,
        "is_active": product.is_active,
    }


def cart_item_to_dict(item):
    return {
        "product_id": item.product_id,
        "product_name": item.product_name,
        "quantity": item.quantity,
        "unit_price": float(item.unit_price),
        "line_total": float(item.unit_price) * item.quantity,
    }


def cart_to_dict(cart, items):
    items_dict = [cart_item_to_dict(item) for item in items]
    total = 0
    for item in items_dict:
        total += item["line_total"]
    return {
        "id": cart.id,
        "user_id": cart.user_id,
        "status": cart.status,
        "items": items_dict,
        "total": round(total, 2),
    }


def invoice_item_to_dict(item):
    return {
        "product_id": item.product_id,
        "product_name": item.product_name,
        "quantity": item.quantity,
        "unit_price": float(item.unit_price),
        "line_total": float(item.line_total),
    }


def invoice_to_dict(invoice):
    return {
        "invoice_number": invoice.invoice_number,
        "user_id": invoice.user_id,
        "cart_id": invoice.cart_id,
        "status": invoice.status,
        "total": float(invoice.total),
        "created_at": invoice.created_at.isoformat(),
    }


def full_invoice_to_dict(invoice):
    invoice_id = invoice.id
    result = invoice_to_dict(invoice)

    items = db_manager.get_invoice_items(invoice_id)
    result["items"] = [invoice_item_to_dict(item) for item in items]

    billing = db_manager.get_billing_address(invoice_id)
    if billing is not None:
        result["billing_address"] = {
            "full_name": billing.full_name,
            "phone": billing.phone,
            "province": billing.province,
            "canton": billing.canton,
            "district": billing.district,
            "exact_address": billing.exact_address,
        }

    payment = db_manager.get_payment(invoice_id)
    if payment is not None:
        result["payment"] = {
            "method": payment.method,
            "sinpe_phone": payment.sinpe_phone,
            "sinpe_reference": payment.sinpe_reference,
            "amount": float(payment.amount),
        }

    return result


def create_token(user):
    expiration = datetime.now(timezone.utc) + timedelta(hours=TOKEN_TTL_HOURS)
    return jwt_manager.encode(
        {"id": user.id, "role": user.role, "exp": expiration}
    )


def is_admin():
    return g.current_user.role == "admin"


def parse_user_payload(data, require_password=True):
    if data is None:
        return None

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "client")

    if username is None or email is None:
        return None

    if require_password and password is None:
        return None

    if role not in ["admin", "client"]:
        return None

    if "@" not in str(email):
        return None

    return {
        "username": username,
        "email": email,
        "password": password,
        "role": role,
    }


def parse_product_payload(data):
    if data is None:
        return None

    name = data.get("name")
    price = data.get("price")
    stock = data.get("stock")

    if name is None or price is None or stock is None:
        return None

    if str(name).strip() == "":
        return None

    try:
        price = float(price)
        stock = int(stock)
    except (TypeError, ValueError):
        return None

    if price < 0 or stock < 0:
        return None

    return {
        "name": name,
        "description": data.get("description"),
        "price": price,
        "stock": stock,
        "category": data.get("category"),
    }


def parse_quantity(data):
    if data is None:
        return None

    quantity = data.get("quantity")
    if quantity is None:
        return None

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return None

    if quantity < 1:
        return None

    return quantity


def parse_checkout_payload(data):
    if data is None:
        return None

    billing = data.get("billing_address")
    payment = data.get("payment")

    if billing is None or payment is None:
        return None

    billing_fields = [
        "full_name",
        "phone",
        "province",
        "canton",
        "district",
        "exact_address",
    ]
    for field in billing_fields:
        value = billing.get(field)
        if value is None or str(value).strip() == "":
            return None

    if payment.get("method") not in ["sinpe", "card", "cash"]:
        return None

    if payment.get("method") == "sinpe" and payment.get("sinpe_phone") is None:
        return None

    return {"billing_address": billing, "payment": payment}


@app.route("/liveness")
def liveness():
    return jsonify(message="Hello, World!")


@app.route("/register", methods=["POST"])
def register():
    payload = parse_user_payload(request.get_json())
    if payload is None:
        return jsonify(error="Bad Request"), 400

    if db_manager.get_user_by_username(payload["username"]) is not None:
        return jsonify(error="Username already exists"), 409

    if db_manager.get_user_by_email(payload["email"]) is not None:
        return jsonify(error="Email already exists"), 409

    result = db_manager.insert_user(
        payload["username"], payload["email"], payload["password"], "client"
    )
    user = db_manager.get_user_by_id(result.id)
    return jsonify(token=create_token(user), user=user_to_dict(user)), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if data is None or data.get("username") is None or data.get("password") is None:
        return jsonify(error="Bad Request"), 400

    user = db_manager.get_user(data.get("username"), data.get("password"))
    if user is None:
        return jsonify(error="Unauthorized"), 401

    return jsonify(token=create_token(user), user=user_to_dict(user))


@app.route("/me")
@require_auth()
def me():
    return jsonify(user_to_dict(g.current_user))


@app.route("/users", methods=["GET"])
@require_auth(["admin"])
def list_users():
    users = db_manager.get_all_users()
    return jsonify([user_to_dict(user) for user in users])


@app.route("/users/<int:user_id>", methods=["GET"])
@require_auth(["admin"])
def get_user(user_id):
    user = db_manager.get_user_by_id(user_id)
    if user is None:
        return jsonify(error="Not Found"), 404

    return jsonify(user_to_dict(user))


@app.route("/users", methods=["POST"])
@require_auth(["admin"])
def create_user():
    payload = parse_user_payload(request.get_json())
    if payload is None:
        return jsonify(error="Bad Request"), 400

    if db_manager.get_user_by_username(payload["username"]) is not None:
        return jsonify(error="Username already exists"), 409

    if db_manager.get_user_by_email(payload["email"]) is not None:
        return jsonify(error="Email already exists"), 409

    result = db_manager.insert_user(
        payload["username"], payload["email"], payload["password"], payload["role"]
    )
    user = db_manager.get_user_by_id(result.id)
    return jsonify(user_to_dict(user)), 201


@app.route("/users/<int:user_id>", methods=["PUT"])
@require_auth(["admin"])
def update_user(user_id):
    data = request.get_json()
    if data is None:
        return jsonify(error="Bad Request"), 400

    if db_manager.get_user_by_id(user_id) is None:
        return jsonify(error="Not Found"), 404

    values = {}
    if data.get("email") is not None:
        if "@" not in str(data.get("email")):
            return jsonify(error="Bad Request"), 400
        values["email"] = data.get("email")

    if data.get("role") is not None:
        if data.get("role") not in ["admin", "client"]:
            return jsonify(error="Bad Request"), 400
        values["role"] = data.get("role")

    if data.get("is_active") is not None:
        values["is_active"] = bool(data.get("is_active"))

    if len(values) == 0:
        return jsonify(error="Bad Request"), 400

    db_manager.update_user(user_id, values)
    user = db_manager.get_user_by_id(user_id)
    return jsonify(user_to_dict(user))


@app.route("/users/<int:user_id>", methods=["DELETE"])
@require_auth(["admin"])
def delete_user(user_id):
    user = db_manager.get_user_by_id(user_id)
    if user is None:
        return jsonify(error="Not Found"), 404

    if user.id == g.current_user.id:
        return jsonify(error="An admin cannot delete itself"), 400

    db_manager.deactivate_user(user_id)
    return jsonify(message="Deleted")


@app.route("/products", methods=["GET"])
@require_auth()
def list_products():
    key = products_cache_key()

    cached = cache_manager.get_data(key)
    if cached is not None:
        return jsonify(json.loads(cached))

    products = db_manager.get_all_products()
    products_dict = [product_to_dict(product) for product in products]
    cache_manager.store_data(
        key, json.dumps(products_dict), time_to_live=PRODUCT_CACHE_TTL
    )
    return jsonify(products_dict)


@app.route("/products/<int:product_id>", methods=["GET"])
@require_auth()
def get_product(product_id):
    key = product_cache_key(product_id)

    cached = cache_manager.get_data(key)
    if cached is not None:
        product_dict = json.loads(cached)
    else:
        product = db_manager.get_product_by_id(product_id)
        if product is None:
            return jsonify(error="Not Found"), 404

        product_dict = product_to_dict(product)
        cache_manager.store_data(
            key, json.dumps(product_dict), time_to_live=PRODUCT_CACHE_TTL
        )

    if product_dict["is_active"] == False and not is_admin():
        return jsonify(error="Not Found"), 404

    return jsonify(product_dict)


@app.route("/products", methods=["POST"])
@require_auth(["admin"])
def create_product():
    payload = parse_product_payload(request.get_json())
    if payload is None:
        return jsonify(error="Bad Request"), 400

    result = db_manager.insert_product(
        payload["name"],
        payload["description"],
        payload["price"],
        payload["stock"],
        payload["category"],
    )
    product = db_manager.get_product_by_id(result.id)
    invalidate_product_cache(product.id)
    return jsonify(product_to_dict(product)), 201


@app.route("/products/<int:product_id>", methods=["PUT"])
@require_auth(["admin"])
def update_product(product_id):
    payload = parse_product_payload(request.get_json())
    if payload is None:
        return jsonify(error="Bad Request"), 400

    if db_manager.get_product_by_id(product_id) is None:
        return jsonify(error="Not Found"), 404

    db_manager.update_product(product_id, payload)
    invalidate_product_cache(product_id)
    product = db_manager.get_product_by_id(product_id)
    return jsonify(product_to_dict(product))


@app.route("/products/<int:product_id>", methods=["DELETE"])
@require_auth(["admin"])
def delete_product(product_id):
    if db_manager.get_product_by_id(product_id) is None:
        return jsonify(error="Not Found"), 404

    db_manager.delete_product(product_id)
    invalidate_product_cache(product_id)
    return jsonify(message="Deleted")


def can_use_cart(cart):
    if is_admin():
        return True
    return cart.user_id == g.current_user.id


@app.route("/carts", methods=["GET"])
@require_auth()
def list_carts():
    if is_admin():
        carts = db_manager.get_all_carts()
    else:
        carts = db_manager.get_carts_by_user(g.current_user.id)

    result = []
    for cart in carts:
        result.append(cart_to_dict(cart, db_manager.get_cart_items(cart.id)))
    return jsonify(result)


@app.route("/carts", methods=["POST"])
@require_auth()
def create_cart():
    result = db_manager.insert_cart(g.current_user.id)
    cart = db_manager.get_cart_by_id(result.id)
    return jsonify(cart_to_dict(cart, [])), 201


@app.route("/carts/<int:cart_id>", methods=["GET"])
@require_auth()
def get_cart(cart_id):
    cart = db_manager.get_cart_by_id(cart_id)
    if cart is None:
        return jsonify(error="Not Found"), 404

    if not can_use_cart(cart):
        return jsonify(error="Forbidden"), 403

    return jsonify(cart_to_dict(cart, db_manager.get_cart_items(cart_id)))


@app.route("/carts/<int:cart_id>", methods=["DELETE"])
@require_auth()
def delete_cart(cart_id):
    cart = db_manager.get_cart_by_id(cart_id)
    if cart is None:
        return jsonify(error="Not Found"), 404

    if not can_use_cart(cart):
        return jsonify(error="Forbidden"), 403

    if cart.status != "open":
        return jsonify(error="Cart is already checked out"), 409

    db_manager.delete_cart(cart_id)
    return jsonify(message="Deleted")


@app.route("/carts/<int:cart_id>/items", methods=["POST"])
@require_auth()
def add_cart_item(cart_id):
    cart = db_manager.get_cart_by_id(cart_id)
    if cart is None:
        return jsonify(error="Not Found"), 404

    if not can_use_cart(cart):
        return jsonify(error="Forbidden"), 403

    if cart.status != "open":
        return jsonify(error="Cart is already checked out"), 409

    data = request.get_json()
    quantity = parse_quantity(data)
    if quantity is None or data.get("product_id") is None:
        return jsonify(error="Bad Request"), 400

    product = db_manager.get_product_by_id(data.get("product_id"))
    if product is None or product.is_active == False:
        return jsonify(error="Not Found"), 404

    db_manager.add_cart_item(cart_id, product.id, quantity)
    return jsonify(cart_to_dict(cart, db_manager.get_cart_items(cart_id))), 201


@app.route("/carts/<int:cart_id>/items/<int:product_id>", methods=["PUT"])
@require_auth()
def set_cart_item(cart_id, product_id):
    cart = db_manager.get_cart_by_id(cart_id)
    if cart is None:
        return jsonify(error="Not Found"), 404

    if not can_use_cart(cart):
        return jsonify(error="Forbidden"), 403

    if cart.status != "open":
        return jsonify(error="Cart is already checked out"), 409

    quantity = parse_quantity(request.get_json())
    if quantity is None:
        return jsonify(error="Bad Request"), 400

    if db_manager.get_cart_item(cart_id, product_id) is None:
        return jsonify(error="Not Found"), 404

    db_manager.set_cart_item_quantity(cart_id, product_id, quantity)
    return jsonify(cart_to_dict(cart, db_manager.get_cart_items(cart_id)))


@app.route("/carts/<int:cart_id>/items/<int:product_id>", methods=["DELETE"])
@require_auth()
def delete_cart_item(cart_id, product_id):
    cart = db_manager.get_cart_by_id(cart_id)
    if cart is None:
        return jsonify(error="Not Found"), 404

    if not can_use_cart(cart):
        return jsonify(error="Forbidden"), 403

    if cart.status != "open":
        return jsonify(error="Cart is already checked out"), 409

    if db_manager.get_cart_item(cart_id, product_id) is None:
        return jsonify(error="Not Found"), 404

    db_manager.delete_cart_item(cart_id, product_id)
    return jsonify(cart_to_dict(cart, db_manager.get_cart_items(cart_id)))


@app.route("/carts/<int:cart_id>/checkout", methods=["POST"])
@require_auth()
def checkout(cart_id):
    cart = db_manager.get_cart_by_id(cart_id)
    if cart is None:
        return jsonify(error="Not Found"), 404

    if not can_use_cart(cart):
        return jsonify(error="Forbidden"), 403

    payload = parse_checkout_payload(request.get_json())
    if payload is None:
        return jsonify(error="Bad Request"), 400

    try:
        invoice_number = db_manager.create_sale(
            cart_id,
            cart.user_id,
            payload["billing_address"],
            payload["payment"],
        )
    except CartNotFoundError:
        return jsonify(error="Not Found"), 404
    except CartClosedError:
        return jsonify(error="Cart is already checked out"), 409
    except InvalidPurchaseError as e:
        return jsonify(error=e.message), 400
    except ProductNotFoundError as e:
        return jsonify(error="Not Found", product_id=e.product_id), 404
    except InsufficientStockError as e:
        return jsonify(
            error="Insufficient stock",
            product_id=e.product_id,
            available=e.available,
            requested=e.requested,
        ), 400

    invoice = db_manager.get_invoice_by_number(invoice_number)
    for item in db_manager.get_invoice_items(invoice.id):
        invalidate_product_cache(item.product_id)

    return jsonify(full_invoice_to_dict(invoice)), 201


@app.route("/invoices", methods=["GET"])
@require_auth()
def list_invoices():
    if is_admin():
        invoices = db_manager.get_all_invoices()
    else:
        invoices = db_manager.get_invoices_by_user(g.current_user.id)

    return jsonify([invoice_to_dict(invoice) for invoice in invoices])


@app.route("/invoices/<invoice_number>", methods=["GET"])
@require_auth()
def get_invoice(invoice_number):
    key = invoice_cache_key(invoice_number)

    cached = cache_manager.get_data(key)
    if cached is not None:
        invoice_dict = json.loads(cached)
    else:
        invoice = db_manager.get_invoice_by_number(invoice_number)
        if invoice is None:
            return jsonify(error="Not Found"), 404

        invoice_dict = full_invoice_to_dict(invoice)
        cache_manager.store_data(
            key, json.dumps(invoice_dict), time_to_live=INVOICE_CACHE_TTL
        )

    if invoice_dict["user_id"] != g.current_user.id and not is_admin():
        return jsonify(error="Forbidden"), 403

    return jsonify(invoice_dict)


@app.route("/invoices/<invoice_number>/refund", methods=["POST"])
@require_auth(["admin"])
def refund_invoice(invoice_number):
    try:
        product_ids = db_manager.refund_sale(invoice_number)
    except InvoiceNotFoundError:
        return jsonify(error="Not Found"), 404
    except InvoiceAlreadyRefundedError:
        return jsonify(error="Invoice was already refunded"), 409

    for product_id in product_ids:
        invalidate_product_cache(product_id)
    invalidate_invoice_cache(invoice_number)

    invoice = db_manager.get_invoice_by_number(invoice_number)
    return jsonify(full_invoice_to_dict(invoice))


@app.route("/invoices/<invoice_number>", methods=["PUT"])
@require_auth(["admin"])
def update_invoice(invoice_number):
    data = request.get_json()
    if data is None or data.get("sinpe_reference") is None:
        return jsonify(error="Bad Request"), 400

    invoice = db_manager.get_invoice_by_number(invoice_number)
    if invoice is None:
        return jsonify(error="Not Found"), 404

    db_manager.update_payment_reference(invoice.id, data.get("sinpe_reference"))
    invalidate_invoice_cache(invoice_number)
    return jsonify(full_invoice_to_dict(invoice))


@app.route("/invoices/<invoice_number>", methods=["DELETE"])
@require_auth(["admin"])
def delete_invoice(invoice_number):
    invoice = db_manager.get_invoice_by_number(invoice_number)
    if invoice is None:
        return jsonify(error="Not Found"), 404

    if invoice.status != "refunded":
        return jsonify(error="Only refunded invoices can be deleted"), 409

    db_manager.delete_invoice(invoice.id)
    invalidate_invoice_cache(invoice_number)
    return jsonify(message="Deleted")


if __name__ == "__main__":
    app.run(debug=True)
