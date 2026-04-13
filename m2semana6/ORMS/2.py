from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    ForeignKey,
    create_engine,
)

metadata_obj = MetaData()

user_table = Table(
    "users",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100), nullable=False),
    Column("email", String(255), nullable=False, unique=True),
)

address_table = Table(
    "addresses",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("street", String(200), nullable=False),
    Column("city", String(100), nullable=False),
    Column("postal_code", String(20), nullable=False),
)

automobile_table = Table(
    "automobiles",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "user_id",
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    ),
    Column("brand", String(50), nullable=False),
    Column("model", String(100), nullable=False),
    Column("year", Integer, nullable=False),
)

DB_URI = "sqlite:///ejercicio_orm.db"
engine = create_engine(DB_URI, echo=True)