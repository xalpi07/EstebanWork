import redis


class CacheManager:
    def __init__(self, host, port, password, *args, **kwargs):
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            password=password,
            socket_connect_timeout=2,
            socket_timeout=2,
            *args,
            **kwargs,
        )
        self.available = False
        try:
            if self.redis_client.ping():
                self.available = True
                print("Connection created succesfully")
        except redis.RedisError as error:
            print(f"Could not connect to Redis: {error}")
            print("La API va a seguir funcionando pero sin cache.")

    def store_data(self, key, value, time_to_live=None):
        if not self.available:
            return
        try:
            if time_to_live is None:
                self.redis_client.set(key, value)
            else:
                self.redis_client.set(key, value, ex=time_to_live)
        except redis.RedisError as error:
            print(f"An error ocurred while storing data in Redis: {error}")

    def check_key(self, key):
        if not self.available:
            return False, None
        try:
            key_exists = self.redis_client.exists(key)
            if key_exists:
                ttl = self.redis_client.ttl(key)
                return True, ttl
            return False, None
        except redis.RedisError as error:
            print(f"An error ocurred while checking a key in Redis: {error}")
            return False, None

    def get_data(self, key):
        if not self.available:
            return None
        try:
            output = self.redis_client.get(key)
            if output is not None:
                result = output.decode("utf-8")
                return result
            else:
                return None
        except redis.RedisError as error:
            print(f"An error ocurred while retrieving data from Redis: {error}")
            return None

    def delete_data(self, key):
        if not self.available:
            return False
        try:
            output = self.redis_client.delete(key)
            return output == 1
        except redis.RedisError as error:
            print(f"An error ocurred while deleting data from Redis: {error}")
            return False

    def delete_data_with_pattern(self, pattern):
        if not self.available:
            return
        try:
            for key in self.redis_client.scan_iter(match=pattern):
                self.delete_data(key)
        except redis.RedisError as error:
            print(f"An error ocurred while deleting data from Redis: {error}")

    def flush(self):
        if not self.available:
            return
        try:
            self.redis_client.flushdb()
        except redis.RedisError as error:
            print(f"An error ocurred while cleaning Redis: {error}")
