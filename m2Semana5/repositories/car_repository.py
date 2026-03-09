from .base_repository import BaseRepository

SCHEMA = "lyfter_car_rental"


class CarRepository(BaseRepository):

    ALLOWED_FILTER_COLUMNS = ["id", "brand", "model", "manufacture_year", "status"]

    def __init__(self, db_manager):
        super().__init__(db_manager, f"{SCHEMA}.cars", "cars")

    def create(self, brand, model, manufacture_year, status="disponible"):
        query = """
            INSERT INTO {table} (brand, model, manufacture_year, status)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """.format(table=self.table_name)
        results = self.db.execute_query(
            query,
            str(brand).strip(),
            str(model).strip(),
            int(manufacture_year),
            status,
        )
        return results[0] if results else None

    def find_by_id(self, car_id):
        query = f"SELECT * FROM {self.table_name} WHERE id = %s"
        results = self.db.execute_query(query, car_id)
        return results[0] if results else None

    def update_status(self, car_id, status):
        query = f"UPDATE {self.table_name} SET status = %s WHERE id = %s"
        self.db.execute_query(query, status, car_id)
        return self.find_by_id(car_id)
