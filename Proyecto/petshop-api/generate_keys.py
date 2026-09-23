import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEYS_DIR = os.path.join(BASE_DIR, "keys")


def generate_keys():
    if not os.path.exists(KEYS_DIR):
        os.makedirs(KEYS_DIR)

    private_path = os.path.join(KEYS_DIR, "private.pem")
    public_path = os.path.join(KEYS_DIR, "public.pem")

    if os.path.exists(private_path) and os.path.exists(public_path):
        print("Las llaves ya existen, no se generan de nuevo.")
        return

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    with open(private_path, "wb") as f:
        f.write(private_bytes)
    with open(public_path, "wb") as f:
        f.write(public_bytes)

    print(f"Llave privada creada en: {private_path}")
    print(f"Llave publica creada en: {public_path}")


if __name__ == "__main__":
    generate_keys()
