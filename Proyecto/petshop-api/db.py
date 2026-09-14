import os
import hashlib
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Numeric,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    create_engine,
    insert,
    select,
    update,
    delete,
    func,
)

DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:fasd89fa7gs98@localhost:5432/petshop",
)

metadata_obj = MetaData()

user_table = Table(
    "users",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("username", String(30), nullable=False, unique=True),
    Column("email", String(255), nullable=False, unique=True),
    Column("password", String(32), nullable=False),
    Column("role", String(20), nullable=False),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime, nullable=False, server_default=func.now()),
    CheckConstraint("role IN ('admin', 'client')", name="ck_users_role"),
)

product_table = Table(
    "products",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(120), nullable=False),
    Column("description", String(255)),
    Column("price", Numeric(12, 2), nullable=False),
    Column("stock", Integer, nullable=False),
    Column("category", String(60)),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime, nullable=False, server_default=func.now()),
    CheckConstraint("price >= 0", name="ck_products_price"),
    CheckConstraint("stock >= 0", name="ck_products_stock"),
)

cart_table = Table(
    "carts",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("user_id", ForeignKey("users.id"), nullable=False),
    Column("status", String(20), nullable=False, default="open"),
    Column("created_at", DateTime, nullable=False, server_default=func.now()),
    CheckConstraint("status IN ('open', 'checked_out')", name="ck_carts_status"),
)

cart_item_table = Table(
    "cart_items",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("cart_id", ForeignKey("carts.id"), nullable=False),
    Column("product_id", ForeignKey("products.id"), nullable=False),
    Column("quantity", Integer, nullable=False),
    UniqueConstraint("cart_id", "product_id", name="uq_cart_items_cart_product"),
    CheckConstraint("quantity >= 1", name="ck_cart_items_quantity"),
)

invoice_table = Table(
    "invoices",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("invoice_number", String(30), nullable=False, unique=True),
    Column("user_id", ForeignKey("users.id"), nullable=False),
    Column("cart_id", ForeignKey("carts.id"), nullable=False, unique=True),
    Column("status", String(20), nullable=False, default="completed"),
    Column("total", Numeric(12, 2), nullable=False),
    Column("created_at", DateTime, nullable=False, server_default=func.now()),
    CheckConstraint("status IN ('completed', 'refunded')", name="ck_invoices_status"),
)

invoice_item_table = Table(
    "invoice_items",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("invoice_id", ForeignKey("invoices.id"), nullable=False),
    Column("product_id", ForeignKey("products.id"), nullable=False),
    Column("quantity", Integer, nullable=False),
    Column("unit_price", Numeric(12, 2), nullable=False),
    Column("line_total", Numeric(12, 2), nullable=False),
    CheckConstraint("quantity >= 1", name="ck_invoice_items_quantity"),
)

billing_address_table = Table(
    "billing_addresses",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("invoice_id", ForeignKey("invoices.id"), nullable=False, unique=True),
    Column("full_name", String(120), nullable=False),
    Column("phone", String(20), nullable=False),
    Column("province", String(60), nullable=False),
    Column("canton", String(60), nullable=False),
    Column("district", String(60), nullable=False),
    Column("exact_address", String(255), nullable=False),
)

payment_table = Table(
    "payments",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("invoice_id", ForeignKey("invoices.id"), nullable=False, unique=True),
    Column("method", String(20), nullable=False),
    Column("sinpe_phone", String(20)),
    Column("sinpe_reference", String(60)),
    Column("amount", Numeric(12, 2), nullable=False),
    Column("paid_at", DateTime, nullable=False, server_default=func.now()),
    CheckConstraint("method IN ('sinpe', 'card', 'cash')", name="ck_payments_method"),
)


class ProductNotFoundError(Exception):
    def __init__(self, product_id):
        self.product_id = product_id
        super().__init__(f"Product {product_id} not found")


class InsufficientStockError(Exception):
    def __init__(self, product_id, available, requested):
        self.product_id = product_id
        self.available = available
        self.requested = requested
        super().__init__(
            f"Insufficient stock for product {product_id}: "
            f"available={available}, requested={requested}"
        )


class CartNotFoundError(Exception):
    def __init__(self, cart_id):
        self.cart_id = cart_id
        super().__init__(f"Cart {cart_id} not found")


class CartClosedError(Exception):
    def __init__(self, cart_id):
        self.cart_id = cart_id
        super().__init__(f"Cart {cart_id} is already checked out")


class InvalidPurchaseError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class InvoiceNotFoundError(Exception):
    def __init__(self, invoice_number):
        self.invoice_number = invoice_number
        super().__init__(f"Invoice {invoice_number} not found")


class InvoiceAlreadyRefundedError(Exception):
    def __init__(self, invoice_number):
        self.invoice_number = invoice_number
        super().__init__(f"Invoice {invoice_number} was already refunded")


def hash_password(password):
    return hashlib.md5(password.encode("utf-8")).hexdigest()


class DB_Manager:
    def __init__(self, db_url=DB_URL):
        self.engine = create_engine(db_url)
        metadata_obj.create_all(self.engine)

    def reset_tables(self):
        metadata_obj.drop_all(self.engine)
        metadata_obj.create_all(self.engine)

    def insert_user(self, username, email, password, role="client"):
        stmt = (
            insert(user_table)
            .returning(user_table.c.id)
            .values(
                username=username,
                email=email,
                password=hash_password(password),
                role=role,
                is_active=True,
            )
        )
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            rows = result.all()
            conn.commit()
        return rows[0]

    def get_user(self, username, password):
        stmt = (
            select(user_table)
            .where(user_table.c.username == username)
            .where(user_table.c.password == hash_password(password))
            .where(user_table.c.is_active == True)
        )
        with self.engine.connect() as conn:
            users = conn.execute(stmt).all()
            if len(users) == 0:
                return None
            return users[0]

    def get_user_by_id(self, user_id):
        stmt = select(user_table).where(user_table.c.id == user_id)
        with self.engine.connect() as conn:
            users = conn.execute(stmt).all()
            if len(users) == 0:
                return None
            return users[0]

    def get_user_by_username(self, username):
        stmt = select(user_table).where(user_table.c.username == username)
        with self.engine.connect() as conn:
            users = conn.execute(stmt).all()
            if len(users) == 0:
                return None
            return users[0]

    def get_user_by_email(self, email):
        stmt = select(user_table).where(user_table.c.email == email)
        with self.engine.connect() as conn:
            users = conn.execute(stmt).all()
            if len(users) == 0:
                return None
            return users[0]

    def get_all_users(self):
        stmt = select(user_table).order_by(user_table.c.id)
        with self.engine.connect() as conn:
            return conn.execute(stmt).all()

    def update_user(self, user_id, values):
        stmt = update(user_table).where(user_table.c.id == user_id).values(**values)
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()
            return result.rowcount > 0

    def deactivate_user(self, user_id):
        return self.update_user(user_id, {"is_active": False})

    def insert_product(self, name, description, price, stock, category):
        stmt = (
            insert(product_table)
            .returning(product_table.c.id)
            .values(
                name=name,
                description=description,
                price=price,
                stock=stock,
                category=category,
                is_active=True,
            )
        )
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            rows = result.all()
            conn.commit()
        return rows[0]

    def get_all_products(self, only_active=True):
        stmt = select(product_table).order_by(product_table.c.id)
        if only_active:
            stmt = stmt.where(product_table.c.is_active == True)
        with self.engine.connect() as conn:
            return conn.execute(stmt).all()

    def get_product_by_id(self, product_id):
        stmt = select(product_table).where(product_table.c.id == product_id)
        with self.engine.connect() as conn:
            products = conn.execute(stmt).all()
            if len(products) == 0:
                return None
            return products[0]

    def update_product(self, product_id, values):
        stmt = (
            update(product_table).where(product_table.c.id == product_id).values(**values)
        )
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()
            return result.rowcount > 0

    def delete_product(self, product_id):
        return self.update_product(product_id, {"is_active": False})

    def insert_cart(self, user_id):
        stmt = (
            insert(cart_table)
            .returning(cart_table.c.id)
            .values(user_id=user_id, status="open")
        )
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            rows = result.all()
            conn.commit()
        return rows[0]

    def get_cart_by_id(self, cart_id):
        stmt = select(cart_table).where(cart_table.c.id == cart_id)
        with self.engine.connect() as conn:
            carts = conn.execute(stmt).all()
            if len(carts) == 0:
                return None
            return carts[0]

    def get_carts_by_user(self, user_id):
        stmt = (
            select(cart_table)
            .where(cart_table.c.user_id == user_id)
            .order_by(cart_table.c.id)
        )
        with self.engine.connect() as conn:
            return conn.execute(stmt).all()

    def get_all_carts(self):
        stmt = select(cart_table).order_by(cart_table.c.id)
        with self.engine.connect() as conn:
            return conn.execute(stmt).all()

    def delete_cart(self, cart_id):
        with self.engine.begin() as conn:
            conn.execute(
                delete(cart_item_table).where(cart_item_table.c.cart_id == cart_id)
            )
            result = conn.execute(delete(cart_table).where(cart_table.c.id == cart_id))
            return result.rowcount > 0

    def get_cart_items(self, cart_id):
        stmt = (
            select(
                cart_item_table.c.id,
                cart_item_table.c.cart_id,
                cart_item_table.c.product_id,
                cart_item_table.c.quantity,
                product_table.c.name,
                product_table.c.price,
            )
            .join(product_table, cart_item_table.c.product_id == product_table.c.id)
            .where(cart_item_table.c.cart_id == cart_id)
            .order_by(cart_item_table.c.id)
        )
        with self.engine.connect() as conn:
            return conn.execute(stmt).all()

    def get_cart_item(self, cart_id, product_id):
        stmt = (
            select(cart_item_table)
            .where(cart_item_table.c.cart_id == cart_id)
            .where(cart_item_table.c.product_id == product_id)
        )
        with self.engine.connect() as conn:
            items = conn.execute(stmt).all()
            if len(items) == 0:
                return None
            return items[0]

    def add_cart_item(self, cart_id, product_id, quantity):
        item = self.get_cart_item(cart_id, product_id)
        if item is None:
            stmt = insert(cart_item_table).values(
                cart_id=cart_id, product_id=product_id, quantity=quantity
            )
        else:
            stmt = (
                update(cart_item_table)
                .where(cart_item_table.c.id == item[0])
                .values(quantity=item[3] + quantity)
            )
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def set_cart_item_quantity(self, cart_id, product_id, quantity):
        stmt = (
            update(cart_item_table)
            .where(cart_item_table.c.cart_id == cart_id)
            .where(cart_item_table.c.product_id == product_id)
            .values(quantity=quantity)
        )
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()
            return result.rowcount > 0

    def delete_cart_item(self, cart_id, product_id):
        stmt = (
            delete(cart_item_table)
            .where(cart_item_table.c.cart_id == cart_id)
            .where(cart_item_table.c.product_id == product_id)
        )
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()
            return result.rowcount > 0

    def next_invoice_number(self, conn):
        last_id = conn.execute(select(func.max(invoice_table.c.id))).scalar()
        if last_id is None:
            last_id = 0
        year = datetime.now().year
        return f"INV-{year}-{last_id + 1:06d}"

    def create_sale(self, cart_id, user_id, billing, payment):
        with self.engine.begin() as conn:
            cart = conn.execute(
                select(cart_table).where(cart_table.c.id == cart_id).with_for_update()
            ).first()

            if cart is None:
                raise CartNotFoundError(cart_id)

            if cart[2] != "open":
                raise CartClosedError(cart_id)

            items = conn.execute(
                select(cart_item_table)
                .where(cart_item_table.c.cart_id == cart_id)
                .order_by(cart_item_table.c.product_id)
            ).all()

            if len(items) == 0:
                raise InvalidPurchaseError("Cart is empty")

            total = Decimal("0.00")
            lines = []

            for item in items:
                product_id = item[2]
                quantity = item[3]

                product = conn.execute(
                    select(product_table)
                    .where(product_table.c.id == product_id)
                    .with_for_update()
                ).first()

                if product is None or product[6] == False:
                    raise ProductNotFoundError(product_id)

                available = product[4]
                if available < quantity:
                    raise InsufficientStockError(product_id, available, quantity)

                unit_price = Decimal(str(product[3]))
                line_total = unit_price * quantity
                total += line_total

                lines.append(
                    {
                        "product_id": product_id,
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "line_total": line_total,
                    }
                )

            invoice_number = self.next_invoice_number(conn)
            invoice_id = conn.execute(
                insert(invoice_table)
                .returning(invoice_table.c.id)
                .values(
                    invoice_number=invoice_number,
                    user_id=user_id,
                    cart_id=cart_id,
                    status="completed",
                    total=total,
                )
            ).all()[0][0]

            for line in lines:
                conn.execute(
                    insert(invoice_item_table).values(
                        invoice_id=invoice_id,
                        product_id=line["product_id"],
                        quantity=line["quantity"],
                        unit_price=line["unit_price"],
                        line_total=line["line_total"],
                    )
                )
                conn.execute(
                    update(product_table)
                    .where(product_table.c.id == line["product_id"])
                    .values(stock=product_table.c.stock - line["quantity"])
                )

            conn.execute(
                insert(billing_address_table).values(
                    invoice_id=invoice_id,
                    full_name=billing["full_name"],
                    phone=billing["phone"],
                    province=billing["province"],
                    canton=billing["canton"],
                    district=billing["district"],
                    exact_address=billing["exact_address"],
                )
            )

            conn.execute(
                insert(payment_table).values(
                    invoice_id=invoice_id,
                    method=payment["method"],
                    sinpe_phone=payment.get("sinpe_phone"),
                    sinpe_reference=payment.get("sinpe_reference"),
                    amount=total,
                )
            )

            conn.execute(
                update(cart_table)
                .where(cart_table.c.id == cart_id)
                .values(status="checked_out")
            )

            return invoice_number

    def refund_sale(self, invoice_number):
        with self.engine.begin() as conn:
            invoice = conn.execute(
                select(invoice_table)
                .where(invoice_table.c.invoice_number == invoice_number)
                .with_for_update()
            ).first()

            if invoice is None:
                raise InvoiceNotFoundError(invoice_number)

            if invoice[4] == "refunded":
                raise InvoiceAlreadyRefundedError(invoice_number)

            invoice_id = invoice[0]
            items = conn.execute(
                select(invoice_item_table).where(
                    invoice_item_table.c.invoice_id == invoice_id
                )
            ).all()

            for item in items:
                conn.execute(
                    update(product_table)
                    .where(product_table.c.id == item[2])
                    .values(stock=product_table.c.stock + item[3])
                )

            conn.execute(
                update(invoice_table)
                .where(invoice_table.c.id == invoice_id)
                .values(status="refunded")
            )

            return [item[2] for item in items]

    def get_invoice_by_number(self, invoice_number):
        stmt = select(invoice_table).where(
            invoice_table.c.invoice_number == invoice_number
        )
        with self.engine.connect() as conn:
            invoices = conn.execute(stmt).all()
            if len(invoices) == 0:
                return None
            return invoices[0]

    def get_invoices_by_user(self, user_id):
        stmt = (
            select(invoice_table)
            .where(invoice_table.c.user_id == user_id)
            .order_by(invoice_table.c.id)
        )
        with self.engine.connect() as conn:
            return conn.execute(stmt).all()

    def get_all_invoices(self):
        stmt = select(invoice_table).order_by(invoice_table.c.id)
        with self.engine.connect() as conn:
            return conn.execute(stmt).all()

    def get_invoice_items(self, invoice_id):
        stmt = (
            select(
                invoice_item_table.c.product_id,
                invoice_item_table.c.quantity,
                invoice_item_table.c.unit_price,
                invoice_item_table.c.line_total,
                product_table.c.name,
            )
            .join(product_table, invoice_item_table.c.product_id == product_table.c.id)
            .where(invoice_item_table.c.invoice_id == invoice_id)
            .order_by(invoice_item_table.c.id)
        )
        with self.engine.connect() as conn:
            return conn.execute(stmt).all()

    def get_billing_address(self, invoice_id):
        stmt = select(billing_address_table).where(
            billing_address_table.c.invoice_id == invoice_id
        )
        with self.engine.connect() as conn:
            rows = conn.execute(stmt).all()
            if len(rows) == 0:
                return None
            return rows[0]

    def get_payment(self, invoice_id):
        stmt = select(payment_table).where(payment_table.c.invoice_id == invoice_id)
        with self.engine.connect() as conn:
            rows = conn.execute(stmt).all()
            if len(rows) == 0:
                return None
            return rows[0]

    def update_payment_reference(self, invoice_id, sinpe_reference):
        stmt = (
            update(payment_table)
            .where(payment_table.c.invoice_id == invoice_id)
            .values(sinpe_reference=sinpe_reference)
        )
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()
            return result.rowcount > 0

    def delete_invoice(self, invoice_id):
        with self.engine.begin() as conn:
            conn.execute(
                delete(payment_table).where(payment_table.c.invoice_id == invoice_id)
            )
            conn.execute(
                delete(billing_address_table).where(
                    billing_address_table.c.invoice_id == invoice_id
                )
            )
            conn.execute(
                delete(invoice_item_table).where(
                    invoice_item_table.c.invoice_id == invoice_id
                )
            )
            result = conn.execute(
                delete(invoice_table).where(invoice_table.c.id == invoice_id)
            )
            return result.rowcount > 0
