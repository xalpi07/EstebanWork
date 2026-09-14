from db import DB_Manager

USERS = [
    ("admin", "admin@petshop.com", "admin123", "admin"),
    ("maria", "maria@petshop.com", "client123", "client"),
    ("carlos", "carlos@petshop.com", "client123", "client"),
]

PRODUCTS = [
    ("Croquetas Adulto Perro 2kg", "Alimento balanceado para perro adulto", 8500, 25, "Alimento"),
    ("Croquetas Gatito 1kg", "Alimento para gatitos de 2 a 12 meses", 6200, 30, "Alimento"),
    ("Arena Sanitaria Gato 10L", "Arena aglomerante con control de olores", 5400, 18, "Higiene"),
    ("Shampoo Antipulgas 500ml", "Shampoo medicado para perros y gatos", 4300, 12, "Higiene"),
    ("Collar Antipulgas Mediano", "Collar con proteccion de 4 meses", 7800, 20, "Accesorios"),
    ("Juguete Hueso de Caucho", "Juguete resistente para masticar", 2900, 40, "Juguetes"),
    ("Rascador para Gato 60cm", "Poste rascador con base de madera", 15900, 6, "Accesorios"),
    ("Cama Perro Talla M", "Cama acolchada lavable", 18500, 8, "Accesorios"),
]


def seed():
    db_manager = DB_Manager()

    print("-" * 50)
    print("Cargando datos de prueba en la base de datos")
    print("-" * 50)

    for username, email, password, role in USERS:
        if db_manager.get_user_by_username(username) is None:
            db_manager.insert_user(username, email, password, role)
            print(f"Usuario creado: {username} ({role})")
        else:
            print(f"El usuario {username} ya existe, se omite.")

    existing = [product[1] for product in db_manager.get_all_products()]

    for name, description, price, stock, category in PRODUCTS:
        if name in existing:
            print(f"El producto '{name}' ya existe, se omite.")
        else:
            db_manager.insert_product(name, description, price, stock, category)
            print(f"Producto creado: {name}")

    print("-" * 50)
    print("Listo. Puedes entrar con admin / admin123")
    print("-" * 50)


if __name__ == "__main__":
    seed()
