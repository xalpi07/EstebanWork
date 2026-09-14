import jwt


class JWT_Manager:
    def __init__(self, private_key_path, public_key_path, algorithm="RS256"):
        with open(private_key_path, "r") as f:
            self.private_key = f.read()
        with open(public_key_path, "r") as f:
            self.public_key = f.read()
        self.algorithm = algorithm

    def encode(self, data):
        try:
            encoded = jwt.encode(data, self.private_key, algorithm=self.algorithm)
            return encoded
        except Exception:
            return None

    def decode(self, token):
        try:
            decoded = jwt.decode(token, self.public_key, algorithms=[self.algorithm])
            return decoded
        except Exception as e:
            print(e)
            return None
