from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Numeric,
    ForeignKey,
    create_engine,
    insert,
    select,
    update,
    delete,
    inspect,
)

metadata_obj = MetaData()

user_table = Table(
    "users",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("username", String(30)),
    Column("password", String),
    Column("role", String(20)),
)

product_table = Table(
    "products",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(100)),
    Column("price", Numeric(10, 2)),
    Column("entry_date", Date),
    Column("quantity", Integer),
)

invoice_table = Table(
    "invoices",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("user_id", ForeignKey("users.id"), nullable=False),
    Column("product_id", ForeignKey("products.id"), nullable=False),
    Column("quantity", Integer, nullable=False),
    Column("total_price", Numeric(10, 2), nullable=False),
    Column("invoice_date", DateTime, nullable=False),
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


class InvalidPurchaseError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class DB_Manager:
    def __init__(self):
        self.engine = create_engine(
            "postgresql+psycopg2://postgres:fasd89fa7gs98@localhost:5432/postgres"
        )
        self.ensure_schema()
        metadata_obj.create_all(self.engine)
        self.ensure_admin()

    def ensure_schema(self):
        inspector = inspect(self.engine)
        if "users" not in inspector.get_table_names():
            return

        columns = {column["name"] for column in inspector.get_columns("users")}
        if "role" not in columns:
            metadata_obj.drop_all(self.engine)

    def ensure_admin(self):
        stmt = select(user_table).where(user_table.c.username == "admin")
        with self.engine.connect() as conn:
            if conn.execute(stmt).first() is None:
                conn.execute(
                    insert(user_table).values(
                        username="admin",
                        password="21232f297a57a5a743894a0e4a801fc3",
                        role="admin",
                    )
                )
                conn.commit()

    def insert_user(self, username, password, role="user"):
        stmt = (
            insert(user_table)
            .returning(user_table.c.id)
            .values(username=username, password=password, role=role)
        )
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()
        return result.all()[0]

    def get_user(self, username, password):
        stmt = (
            select(user_table)
            .where(user_table.c.username == username)
            .where(user_table.c.password == password)
        )
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            users = result.all()
            if len(users) == 0:
                return None
            return users[0]

    def get_user_by_id(self, id):
        stmt = select(user_table).where(user_table.c.id == id)
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            users = result.all()
            if len(users) == 0:
                return None
            return users[0]

    def insert_product(self, name, price, entry_date, quantity):
        stmt = (
            insert(product_table)
            .returning(product_table.c.id)
            .values(
                name=name,
                price=price,
                entry_date=entry_date,
                quantity=quantity,
            )
        )
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()
        return result.all()[0]

    def get_all_products(self):
        stmt = select(product_table)
        with self.engine.connect() as conn:
            return conn.execute(stmt).all()

    def get_product_by_id(self, product_id):
        stmt = select(product_table).where(product_table.c.id == product_id)
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            products = result.all()
            if len(products) == 0:
                return None
            return products[0]

    def update_product(self, product_id, name, price, entry_date, quantity):
        stmt = (
            update(product_table)
            .where(product_table.c.id == product_id)
            .values(name=name, price=price, entry_date=entry_date, quantity=quantity)
        )
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()
            return result.rowcount > 0

    def delete_product(self, product_id):
        stmt = delete(product_table).where(product_table.c.id == product_id)
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()
            return result.rowcount > 0

    def create_purchase(self, user_id, items):
        if not items:
            raise InvalidPurchaseError("Purchase must include at least one product")

        with self.engine.begin() as conn:
            invoices = []
            purchase_total = Decimal("0")
            invoice_date = datetime.now()

            for item in items:
                product_id = item.get("product_id")
                quantity = item.get("quantity")

                if product_id is None or quantity is None:
                    raise InvalidPurchaseError(
                        "Each item must include product_id and quantity"
                    )

                try:
                    product_id = int(product_id)
                    quantity = int(quantity)
                except (TypeError, ValueError):
                    raise InvalidPurchaseError(
                        "product_id and quantity must be integers"
                    )

                if quantity <= 0:
                    raise InvalidPurchaseError("quantity must be greater than 0")

                product = conn.execute(
                    select(product_table).where(product_table.c.id == product_id)
                ).first()

                if product is None:
                    raise ProductNotFoundError(product_id)

                if product.quantity < quantity:
                    raise InsufficientStockError(
                        product_id, product.quantity, quantity
                    )

                line_total = Decimal(str(product.price)) * quantity
                purchase_total += line_total

                conn.execute(
                    update(product_table)
                    .where(product_table.c.id == product_id)
                    .values(quantity=product.quantity - quantity)
                )

                invoice_id = conn.execute(
                    insert(invoice_table)
                    .returning(invoice_table.c.id)
                    .values(
                        user_id=user_id,
                        product_id=product_id,
                        quantity=quantity,
                        total_price=line_total,
                        invoice_date=invoice_date,
                    )
                ).all()[0][0]

                invoices.append(
                    {
                        "invoice_id": invoice_id,
                        "product_id": product_id,
                        "quantity": quantity,
                        "total_price": float(line_total),
                    }
                )

            return {
                "invoices": invoices,
                "total_price": float(purchase_total),
            }

    def get_invoices_by_user(self, user_id):
        stmt = select(invoice_table).where(invoice_table.c.user_id == user_id)
        with self.engine.connect() as conn:
            return conn.execute(stmt).all()
