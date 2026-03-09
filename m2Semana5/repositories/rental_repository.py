from .base_repository import BaseRepository

SCHEMA = "lyfter_car_rental"


class RentalRepository(BaseRepository):

    ALLOWED_FILTER_COLUMNS = ["id", "user_id", "automobile_id", "rental_date", "status"]

    def __init__(self, db_manager):
        super().__init__(db_manager, f"{SCHEMA}.rentals", "rentals")

    def create(self, user_id, automobile_id):
        query = """
            INSERT INTO {table} (user_id, automobile_id, status)
            VALUES (%s, %s, 'activo')
            RETURNING *
        """.format(table=self.table_name)
        results = self.db.execute_query(query, user_id, automobile_id)
        return results[0] if results else None

    def find_by_id(self, rental_id):
        query = f"SELECT * FROM {self.table_name} WHERE id = %s"
        results = self.db.execute_query(query, rental_id)
        return results[0] if results else None

    def update_status(self, rental_id, status):
        query = f"UPDATE {self.table_name} SET status = %s WHERE id = %s"
        self.db.execute_query(query, status, rental_id)
        return self.find_by_id(rental_id)
