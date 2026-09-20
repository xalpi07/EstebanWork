# Decisiones tecnicas

Este documento registra las decisiones de diseno de la Petshop API: que se decidio,
por que, que implica para quien trabaje sobre el proyecto y donde encontrar cada
cosa en el codigo. Las alternativas evaluadas y descartadas estan al final.

## 1. Organizacion en archivos planos

El proyecto se reparte en cinco archivos, cada uno con una responsabilidad unica:

| Archivo | Responsabilidad |
|---|---|
| `app.py` | rutas HTTP, validacion de los JSON de entrada y serializacion de las respuestas |
| `db.py` | definicion de tablas, consultas y errores de negocio |
| `auth.py` | verificacion del token y del rol |
| `cache.py` | comunicacion con Redis |
| `JWT_Manager.py` | firma y verificacion de tokens |

La ventaja practica es que el punto de entrada de cualquier cambio es predecible:
una consulta que devuelve mal los datos se corrige en `db.py`, un permiso mal
aplicado en `auth.py`, un campo que falta en la respuesta en `app.py`.

No se subdividio en paquetes con subcarpetas porque, para el tamano actual del
proyecto, la indireccion extra costaria mas de lo que aporta.

## 2. Acceso a datos exclusivamente por ORM

Todas las operaciones contra PostgreSQL pasan por **SQLAlchemy Core**, usando
`Table` y `MetaData`. Las tablas se crean con `metadata_obj.create_all()` y las
consultas se construyen con `select()`, `insert()`, `update()` y `delete()`. No hay
scripts `.sql` operativos ni pasos manuales en pgAdmin.

La unica sentencia que se ejecuta fuera del ORM es `CREATE DATABASE`, porque
SQLAlchemy necesita conectarse a una base que ya exista.

**Core en lugar del ORM declarativo.** Se eligio Core (tablas y expresiones) sobre
el patron declarativo con clases mapeadas y `sessionmaker`. Las expresiones de Core
se traducen casi uno a uno al SQL que se ejecuta, lo que hace mas facil razonar
sobre el costo de cada consulta y depurar el comportamiento real contra la base.

## 3. Roles y control de acceso

Existen dos roles, `admin` y `client`, almacenados en la columna `role` de `users`
y protegidos por un `CHECK` que impide guardar cualquier otro valor.

El decorador `require_auth()` de `auth.py` centraliza el control: extrae el token
del header `Authorization`, lo verifica, carga el usuario y compara su rol contra
la lista de roles permitidos de cada ruta.

| Situacion | Respuesta |
|---|---|
| No llega token, o el token es invalido o esta vencido | `401 Unauthorized` |
| El usuario fue desactivado (`is_active = False`) | `401 Unauthorized` |
| El token es valido pero el rol no tiene permiso | `403 Forbidden` |

| Rol | Alcance |
|---|---|
| `admin` | crear, editar y desactivar productos y usuarios; consultar todas las facturas; procesar devoluciones |
| `client` | consultar el catalogo, administrar sus propios carritos, facturar y consultar sus propias facturas |

Dos reglas refuerzan el modelo:

- `POST /register` crea siempre un `client`, incluso si el cuerpo de la peticion
  incluye `"role": "admin"`. Los administradores se crean unicamente mediante
  `seed.py` o desde `POST /users` con una sesion de admin.
- La validacion del estado activo ocurre en cada peticion, no solo al emitir el
  token. Desactivar un usuario invalida de inmediato los tokens que ya tenia.

## 4. El checkout como accion sobre el carrito

El modelo de permisos plantea una tension: el cliente tiene que poder concretar una
venta, pero la creacion y modificacion de facturas esta reservada al
administrador.

La solucion fue no exponer un `POST /invoices` generico. El cliente factura su
propio carrito mediante `POST /carts/<id>/checkout`, y es la API la que construye la
factura leyendo los precios desde la base.

El cliente decide *que* comprar, pero nunca *cuanto* se le cobra. Los montos no
viajan en la peticion, se calculan en el servidor, de modo que no existe forma de
manipularlos desde el cliente.

## 5. Carritos persistentes y reutilizables

Un usuario puede mantener varios carritos en estado `open` simultaneamente y
recuperarlos con `GET /carts`. Facturar un carrito no lo elimina: cambia su estado
a `checked_out` y lo deja vinculado a la factura, preservando el registro de que se
compro y en que momento.

Las dos operaciones sobre las lineas tienen semantica distinta a proposito:

| Operacion | Comportamiento |
|---|---|
| `POST /carts/<id>/items` | suma la cantidad a la que ya existia |
| `PUT /carts/<id>/items/<product_id>` | reemplaza la cantidad por el valor enviado |

La distincion corresponde a dos acciones diferentes del usuario: agregar algo al
carrito no es lo mismo que corregir una cantidad ya cargada.

## 6. La venta como transaccion atomica

El checkout completo ocurre dentro de un unico bloque
`with self.engine.begin() as conn:` en `db.py`. Dentro de esa transaccion se
valida el carrito, se verifica el stock, se crea la factura y sus lineas, se rebaja
el inventario, se guardan la direccion y el pago, y se cierra el carrito.

**Atomicidad.** Si un solo producto no tiene stock suficiente se lanza
`InsufficientStockError` y SQLAlchemy revierte la transaccion entera. No quedan
facturas parciales ni inventario descontado de los productos que si alcanzaban. La
prueba `test_checkout_without_enough_stock_does_not_change_anything` verifica que
el stock y el estado del carrito permanezcan intactos tras un intento fallido.

**Concurrencia.** Los productos se leen con `.with_for_update()`, que genera un
`SELECT ... FOR UPDATE` en PostgreSQL y bloquea la fila hasta el final de la
transaccion. Esto evita que dos compras simultaneas lean el mismo stock y ambas lo
consideren disponible.

**Prevencion de interbloqueos.** Las lineas se recorren ordenadas por
`product_id`. Si dos ventas concurrentes compiten por los mismos productos,
solicitan los bloqueos en el mismo orden, lo que descarta el escenario clasico de
deadlock en que cada transaccion espera el recurso que la otra ya tomo.

## 7. Devoluciones

`POST /invoices/<numero>/refund` esta restringido a administradores y opera sobre
la factura completa. Reintegra al inventario la cantidad de cada linea y marca la
factura como `refunded`.

Intentar devolver una factura ya devuelta responde `409 Conflict`. La validacion es
necesaria: sin ella, cada llamada repetida volveria a sumar stock que nunca salio
del almacen.

Las devoluciones parciales por linea quedaron fuera del alcance. Seria la extension
natural del modulo, y `invoice_items` ya tiene la granularidad necesaria para
soportarlas.

## 8. Estrategia de cache

| Llave | Contenido | TTL | Criterio |
|---|---|---|---|
| `products:all` | catalogo de productos activos | 300 s | endpoint de lectura mas frecuente, con datos que cambian poco |
| `product:<id>` | detalle de un producto | 300 s | mismo perfil de uso que el listado |
| `invoice:<numero>` | factura completa con lineas, direccion y pago | 600 s | una factura emitida es practicamente inmutable |

**Invalidacion explicita.** Las llaves se eliminan activamente cuando el dato
cambia: al crear, editar o desactivar un producto, despues de cada venta y despues
de cada devolucion. El TTL no es el mecanismo principal de coherencia, sino una red
de seguridad ante una invalidacion que pudiera faltar.

**Datos que no se cachean.** Los carritos cambian en cada interaccion y pertenecen
a un solo usuario, asi que cachearlos aportaria poco y arriesgaria mostrar
contenido desactualizado. Los listados de facturas y el login tampoco se cachean.

**El stock nunca se sirve desde cache al vender.** Esta es la regla central de la
estrategia. Dentro de la transaccion de venta, el inventario se lee siempre desde
PostgreSQL con `FOR UPDATE`. El cache existe unicamente para acelerar la lectura
del catalogo; jamas participa en una decision de negocio.

**Degradacion sin Redis.** `CacheManager` verifica la conexion al inicializarse. Si
falla, marca el cache como no disponible y todos sus metodos retornan de inmediato
sin intentar reconectar. Para la API el resultado es indistinguible de un cache
vacio: las consultas van a PostgreSQL y el servicio sigue operando. El cliente de
Redis usa un timeout de 2 segundos para que una instancia caida no bloquee el
arranque.

## 9. Autenticacion con JWT RS256

Los tokens se firman con RSA usando un par de llaves: la privada firma y la publica
verifica. El payload contiene el `id` y el `role` del usuario, mas un claim `exp`
con la fecha de vencimiento.

El vencimiento se fija en 8 horas mediante la constante `TOKEN_TTL_HOURS` de
`app.py`. Sin ese claim un token robado serviria para siempre, porque la firma RSA
no caduca por si sola. PyJWT valida `exp` de forma automatica al decodificar, asi
que un token vencido hace que `JWT_Manager.decode()` retorne `None` y el decorador
`require_auth()` responda `401 Unauthorized`, el mismo camino que un token invalido.
No existe mecanismo de refresh: al vencer, el cliente vuelve a autenticarse contra
`/login`.

RS256 se eligio sobre HS256 porque permite distribuir la llave publica a otros
servicios para que validen tokens sin poder emitirlos. Con un algoritmo simetrico,
cualquier componente capaz de verificar tambien podria falsificar.

Las llaves se generan con `python generate_keys.py`, que produce
`keys/private.pem` y `keys/public.pem`. El directorio `keys/*.pem` esta en
`.gitignore`: la llave privada no debe llegar al repositorio, y cada entorno genera
la suya.

## 10. Hash de contrasenas con MD5

Las contrasenas se almacenan con `hashlib.md5()`.

**Esta eleccion no es apta para produccion.** MD5 es un algoritmo rapido, disenado
para verificar integridad y no para proteger credenciales, y aqui se aplica sin
salt, lo que lo deja expuesto a tablas precomputadas. Un sistema real debe usar
`bcrypt`, `scrypt` o `argon2`, que son deliberadamente lentos e incorporan salt.

La limitacion se documenta de forma explicita porque es el primer punto a corregir
antes de exponer el servicio a usuarios reales. El cambio esta acotado: solo
afecta a la funcion `hash_password()` de `db.py`.

## 11. Borrado logico de productos

`DELETE /products/<id>` no elimina la fila: establece `is_active = False`.

Un borrado fisico romperia las claves foraneas de `invoice_items` y dejaria
facturas historicas apuntando a productos inexistentes. El borrado logico preserva
ese historial.

Un producto desactivado desaparece del catalogo que ve el cliente y responde `404`
si lo consulta directamente, pero el administrador si puede recuperarlo por id.

## 12. Numeracion de facturas

El formato es `INV-<anio>-<consecutivo de 6 digitos>`, por ejemplo
`INV-2026-000001`. El consecutivo se calcula dentro de la transaccion de venta a
partir de `max(invoices.id) + 1`.

Se expone este numero, y no el `id` interno, porque es legible y facil de dictar
por telefono o copiar de un comprobante. Por eso `GET /invoices/<numero>` busca por
`invoice_number`.

## 13. Pruebas

La suite tiene 82 pruebas con `pytest`, organizadas por area: `test_auth.py`,
`test_products.py`, `test_carts.py`, `test_sales.py`, `test_invoices.py`,
`test_permissions.py` y `test_cache.py`. Cada area cubre tanto los casos exitosos
como los de error, verificando el codigo HTTP y el mensaje devuelto.

**Aislamiento.** Las pruebas corren contra una base dedicada (`petshop_test`) y la
base 15 de Redis. `helpers.start()` reconstruye el esquema y limpia el cache antes
de cada prueba, de modo que ninguna dependa del estado que dejo la anterior y el
orden de ejecucion sea irrelevante.

**Sin Redis disponible.** Las pruebas de `test_cache.py` comprueban primero si hay
cache y se omiten si no lo hay. Las otras 74 siguen corriendo, lo que permite
validar la logica de negocio sin levantar Redis.

**Reporte.** `python run_tests.py` ejecuta la suite, resume los resultados en
consola y escribe `test_report.txt` con el conteo y la salida completa de pytest.

## 14. Alternativas evaluadas y descartadas

| Alternativa | Motivo del descarte |
|---|---|
| Escribir SQL directo o administrar la base desde pgAdmin | dejaria el esquema fuera del control de versiones y haria el acceso a datos imposible de auditar desde el codigo |
| ORM declarativo con `sessionmaker` | Core hace mas transparente el SQL que se ejecuta |
| Un unico carrito abierto por usuario | impediria el requisito de mantener y retomar varios carritos |
| `POST /invoices` generico para el cliente | permitiria que el cliente definiera los montos de su propia factura |
| Cachear carritos | cambian en cada interaccion; el riesgo de datos obsoletos supera la ganancia |
| Descontar stock leyendo desde cache | abriria la puerta a vender inventario inexistente |
| Devoluciones parciales por linea | fuera del alcance de esta version |
| Borrado fisico de productos | dejaria facturas historicas sin producto asociado |
| Guardar direccion y pago dentro de `invoices` | incumpliria la tercera forma normal |
| FastAPI o Django | Flask cubre el alcance sin agregar dependencias ni capas extra |
