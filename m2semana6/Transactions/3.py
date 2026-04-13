def realizar_retorno(conn, factura_id: int) -> None:
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT producto_id, cantidad, estado
                FROM facturas
                WHERE id = %s
                FOR UPDATE
                """,
                (factura_id,),
            )
            fila = cur.fetchone()
            if fila is None:
                raise ValueError("La factura no existe en la base de datos.")
            producto_id, cantidad, estado = fila
            if estado == "retornada":
                raise ValueError("La factura ya fue marcada como retornada.")

            cur.execute(
                """
                UPDATE productos
                SET stock = stock + %s
                WHERE id = %s
                """,
                (cantidad, producto_id),
            )
            if cur.rowcount == 0:
                raise ValueError("El producto asociado a la factura no existe.")

            cur.execute(
                """
                UPDATE facturas
                SET estado = 'retornada'
                WHERE id = %s
                """,
                (factura_id,),
            )