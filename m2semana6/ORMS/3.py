import importlib.util
from pathlib import Path

from sqlalchemy import inspect

REQUIRED_TABLES = frozenset({"users", "addresses", "automobiles"})


def tables_exist(engine):
    inspector = inspect(engine)
    existing = set(inspector.get_table_names())
    return REQUIRED_TABLES <= existing


if __name__ == "__main__":
    _spec = importlib.util.spec_from_file_location(
        "schema_m2semana6", Path(__file__).resolve().parent / "2.py"
    )
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)

    engine = _mod.engine
    metadata_obj = _mod.metadata_obj

    if tables_exist(engine):
        print("Las tablas requeridas ya existen.")
    else:
        print("Faltan tablas; creando con metadata_obj.create_all(engine)...")
        metadata_obj.create_all(engine)
        print("Tablas creadas.")
