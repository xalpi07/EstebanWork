from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    text,
)
from sqlalchemy.sql import func

metadata_obj = MetaData()

usuario_table = Table(
    "usuarios",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("nombre", String(200), nullable=False),
    Column("email", String(255), nullable=False, unique=True),
)

producto_table = Table(
    "productos",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("nombre", String(200), nullable=False),
    Column("precio", Numeric(12, 2), nullable=False),
    Column("stock", Integer, nullable=False, server_default=text("0")),
    CheckConstraint("precio >= 0", name="ck_productos_precio"),
    CheckConstraint("stock >= 0", name="ck_productos_stock"),
)

factura_table = Table(
    "facturas",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "usuario_id",
        Integer,
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column(
        "producto_id",
        Integer,
        ForeignKey("productos.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column("cantidad", Integer, nullable=False),
    Column("precio_unitario", Numeric(12, 2), nullable=False),
    Column("total", Numeric(12, 2), nullable=False),
    Column("estado", String(20), nullable=False, server_default=text("'completada'")),
    Column("creado_en", DateTime, nullable=False, server_default=func.now()),
    CheckConstraint("cantidad > 0", name="ck_facturas_cantidad"),
    CheckConstraint("precio_unitario >= 0", name="ck_facturas_precio_unitario"),
    CheckConstraint("total >= 0", name="ck_facturas_total"),
    CheckConstraint(
        "estado IN ('completada', 'retornada')",
        name="ck_facturas_estado",
    ),
    Index("idx_facturas_usuario", "usuario_id"),
    Index("idx_facturas_producto", "producto_id"),
    Index("idx_facturas_estado", "estado"),
)
