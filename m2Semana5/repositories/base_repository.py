class BaseRepository:

    ALLOWED_FILTER_COLUMNS = []

    def __init__(self, db_manager, table_name, entity_name):
        self.db = db_manager
        self.table_name = table_name
        self.entity_name = entity_name

    def find_all(self, filters=None):
        filters = filters or {}
        valid_filters = {
            k: v for k, v in filters.items()
            if k in self.ALLOWED_FILTER_COLUMNS and v is not None and v != ""
        }
        if not valid_filters:
            query = f"SELECT * FROM {self.table_name}"
            results = self.db.execute_query(query)
        else:
            conditions = " AND ".join([f"{col} = %s" for col in sorted(valid_filters.keys())])
            query = f"SELECT * FROM {self.table_name} WHERE {conditions}"
            params = [valid_filters[k] for k in sorted(valid_filters.keys())]
            results = self.db.execute_query(query, *params)
        return results or []
