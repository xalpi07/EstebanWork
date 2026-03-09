from .base_repository import BaseRepository

SCHEMA = "lyfter_car_rental"


class UserRepository(BaseRepository):

    ALLOWED_FILTER_COLUMNS = ["id", "name", "email", "username", "date_of_birth", "account_status"]

    def __init__(self, db_manager):
        super().__init__(db_manager, f"{SCHEMA}.users", "users")

    def create(self, name, email, username, password, date_of_birth, account_status="active"):
        query = """
            INSERT INTO {table} (name, email, username, password, date_of_birth, account_status)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
        """.format(table=self.table_name)
        results = self.db.execute_query(
            query,
            name.strip(),
            email.strip(),
            username.strip(),
            password,
            date_of_birth,
            account_status,
        )
        return results[0] if results else None

    def find_by_id(self, user_id):
        query = f"SELECT * FROM {self.table_name} WHERE id = %s"
        results = self.db.execute_query(query, user_id)
        return results[0] if results else None

    def update_account_status(self, user_id, account_status):
        query = f"UPDATE {self.table_name} SET account_status = %s WHERE id = %s"
        self.db.execute_query(query, account_status, user_id)

    def flag_moroso(self, user_id):
        self.update_account_status(user_id, "moroso")
