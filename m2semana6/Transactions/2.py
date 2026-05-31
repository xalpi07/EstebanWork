def realizar_compra(conn, usuario_id: int, producto_id: int, cantidad: int) -> int:
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor que cero.")

    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT stock, precio
                FROM productos
                WHERE id = %s
                FOR UPDATE
                """,
                (producto_id,),
            )
            fila = cur.fetchone()
            if fila is None:
                raise ValueError("El producto no existe.")
            stock, precio = fila
            if stock < cantidad:
                raise ValueError("Stock insuficiente para la cantidad solicitada.")

            cur.execute("SELECT 1 FROM usuarios WHERE id = %s", (usuario_id,))
            if cur.fetchone() is None:
                raise ValueError("El usuario no existe.")

            precio_unitario = precio
            total = precio_unitario * cantidad
            cur.execute(
                """
                INSERT INTO facturas (
                    usuario_id, producto_id, cantidad,
                    precio_unitario, total, estado
                )
                VALUES (%s, %s, %s, %s, %s, 'completada')
                RETURNING id
                """,
                (usuario_id, producto_id, cantidad, precio_unitario, total),
            )
            factura_id = cur.fetchone()[0]

            cur.execute(
                """
                UPDATE productos
                SET stock = stock - %s
                WHERE id = %s
                """,
                (cantidad, producto_id),
            )

    return factura_id