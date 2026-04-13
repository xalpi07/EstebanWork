import importlib.util
from pathlib import Path

from sqlalchemy import insert, select, update, delete

_spec = importlib.util.spec_from_file_location(
    "schema_m2semana6", Path(__file__).resolve().parent / "2.py"
)
_schema = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_schema)

user_table = _schema.user_table
address_table = _schema.address_table
automobile_table = _schema.automobile_table


class UserManager:
    def __init__(self, engine):
        self.engine = engine

    def create(self, name, email):
        stmt = insert(user_table).values(name=name, email=email)
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()
            nuevo_id = result.inserted_primary_key[0]
        return nuevo_id

    def modify(self, user_id, name, email):
        stmt = (
            update(user_table)
            .where(user_table.c.id == user_id)
            .values(name=name, email=email)
        )
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def delete(self, user_id):
        stmt = delete(user_table).where(user_table.c.id == user_id)
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def get_all(self):
        stmt = select(user_table)
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            return result.all()


class AutomobileManager:
    def __init__(self, engine):
        self.engine = engine

    def create(self, brand, model, year, user_id=None):
        stmt = insert(automobile_table).values(
            brand=brand,
            model=model,
            year=year,
            user_id=user_id,
        )
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()
            nuevo_id = result.inserted_primary_key[0]
        return nuevo_id

    def modify(self, automobile_id, brand, model, year, user_id):
        stmt = (
            update(automobile_table)
            .where(automobile_table.c.id == automobile_id)
            .values(brand=brand, model=model, year=year, user_id=user_id)
        )
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def delete(self, automobile_id):
        stmt = delete(automobile_table).where(automobile_table.c.id == automobile_id)
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def associate_to_user(self, automobile_id, user_id):
        stmt = (
            update(automobile_table)
            .where(automobile_table.c.id == automobile_id)
            .values(user_id=user_id)
        )
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def get_all(self):
        stmt = select(automobile_table)
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            return result.all()


class AddressManager:
    def __init__(self, engine):
        self.engine = engine

    def create(self, user_id, street, city, postal_code):
        stmt = insert(address_table).values(
            user_id=user_id,
            street=street,
            city=city,
            postal_code=postal_code,
        )
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()
            nuevo_id = result.inserted_primary_key[0]
        return nuevo_id

    def modify(self, address_id, user_id, street, city, postal_code):
        stmt = (
            update(address_table)
            .where(address_table.c.id == address_id)
            .values(
                user_id=user_id,
                street=street,
                city=city,
                postal_code=postal_code,
            )
        )
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def delete(self, address_id):
        stmt = delete(address_table).where(address_table.c.id == address_id)
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def get_all(self):
        stmt = select(address_table)
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            return result.all()


if __name__ == "__main__":
    eng = _schema.engine
    users = UserManager(eng)
    cars = AutomobileManager(eng)
    addrs = AddressManager(eng)
    print("Usuarios:", users.get_all())
    print("Automóviles:", cars.get_all())
    print("Direcciones:", addrs.get_all())
