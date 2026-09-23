# Petshop API

API REST para una tienda de articulos para mascotas. Sustituye el proceso manual de
cobrar por SINPE y registrar las ventas en una hoja de Excel por un backend con
usuarios y roles, catalogo con control de inventario, carritos que se pueden
retomar, y facturas que conservan su direccion de cobro y su forma de pago.

Construida con Flask, SQLAlchemy Core, PostgreSQL y Redis.

## Estructura del proyecto

| Archivo | Responsabilidad |
|---|---|
| `app.py` | rutas HTTP, validacion de las peticiones y formato de las respuestas |
| `db.py` | definicion de tablas, clase `DB_Manager` y errores de negocio |
| `auth.py` | decorador `require_auth`, que valida token y rol |
| `JWT_Manager.py` | emision y verificacion de tokens JWT con RS256 |
| `cache.py` | clase `CacheManager`, que encapsula el acceso a Redis |
| `seed.py` | carga usuarios y productos de ejemplo |
| `generate_keys.py` | genera el par de llaves RSA que requiere el JWT |
| `run_tests.py` | ejecuta la suite de pruebas y genera el reporte |
| `tests/` | pruebas unitarias por area funcional |
| `docs/` | modelo de datos y decisiones tecnicas |

## Requisitos

- Python 3.11 o superior
- PostgreSQL accesible en `localhost:5432`
- Redis (opcional: sin el, la API funciona sin cache)

## Puesta en marcha

### 1. Crear las bases de datos

```sql
CREATE DATABASE petshop;
CREATE DATABASE petshop_test;
```

`petshop_test` la usan exclusivamente las pruebas, que borran y recrean sus tablas
en cada ejecucion. Mantenerla separada evita perder los datos de desarrollo.

Las tablas no se crean manualmente: `DB_Manager` invoca
`metadata_obj.create_all()` al instanciarse, de modo que basta arrancar la API o
cualquier script para que el esquema quede listo.

### 2. Levantar Redis

```bash
docker run -d --name petshop-redis -p 16379:6379 redis:7-alpine
```

El puerto 16379 se usa en lugar del 6379 habitual porque en Windows el rango 6306
a 6405 suele quedar reservado por Hyper-V, lo que impide a Docker publicar ahi. El
rango reservado se consulta con:

```powershell
netsh interface ipv4 show excludedportrange protocol=tcp
```

En un entorno sin ese conflicto puede usarse el puerto estandar ajustando
`REDIS_PORT`.

### 3. Instalar las dependencias

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Generar las llaves del JWT

```bash
python generate_keys.py
```

Genera `keys/private.pem` y `keys/public.pem`. El directorio esta en `.gitignore`:
la llave privada no se versiona y cada entorno genera la suya.

### 5. Cargar datos de ejemplo

```bash
python seed.py
```

El script es idempotente: puede ejecutarse varias veces sin duplicar registros.
Crea tres usuarios y ocho productos.

| Usuario | Contrasena | Rol |
|---|---|---|
| admin | admin123 | admin |
| maria | client123 | client |
| carlos | client123 | client |

### 6. Arrancar la API

```bash
python app.py
```

Queda disponible en `http://127.0.0.1:5000`. El endpoint `GET /liveness` confirma
que el servicio responde.

## Variables de entorno

Todas son opcionales. Sin definirlas, la aplicacion usa valores por defecto
orientados a un entorno de desarrollo local.

| Variable | Valor por defecto | Uso |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg2://postgres:...@localhost:5432/petshop` | base principal |
| `TEST_DATABASE_URL` | `postgresql+psycopg2://postgres:...@localhost:5432/petshop_test` | base de pruebas |
| `REDIS_HOST` | `127.0.0.1` | host de Redis |
| `REDIS_PORT` | `16379` | puerto de Redis |
| `REDIS_PASSWORD` | vacio | contrasena de Redis |
| `REDIS_DB` | `0` | numero de base; las pruebas fuerzan la 15 |

## Pruebas

```bash
python run_tests.py
```

El script ejecuta pytest, resume los resultados en consola y escribe
`test_report.txt` con el conteo y la salida completa.

La suite tiene 82 pruebas que cubren tanto los flujos exitosos como los de error:
token invalido, rol sin permiso, stock insuficiente, carrito ya facturado, factura
devuelta dos veces y acceso a recursos de otro usuario.

Cada prueba comienza con `helpers.start()`, que recrea el esquema de
`petshop_test` y limpia el cache, de modo que ninguna dependa del estado que dejo
la anterior.

Si Redis no esta disponible, las pruebas de `test_cache.py` se omiten
automaticamente y las 74 restantes siguen ejecutandose. La API se comporta igual:
al no haber cache, las consultas van directo a PostgreSQL.

## Endpoints

Todas las rutas excepto `/liveness`, `/register` y `/login` requieren el header
`Authorization: Bearer <token>`.

El token vence a las 8 horas de emitido, segun la constante `TOKEN_TTL_HOURS` de
`app.py`. Una vez vencido las rutas protegidas responden `401` y hay que volver a
llamar a `/login` para obtener uno nuevo.

### Autenticacion

| Metodo | Ruta | Acceso |
|---|---|---|
| POST | `/register` | publico; el usuario creado siempre es `client` |
| POST | `/login` | publico |
| GET | `/me` | cualquier usuario autenticado |

### Usuarios

| Metodo | Ruta | Acceso |
|---|---|---|
| GET | `/users` | admin |
| GET | `/users/<id>` | admin |
| POST | `/users` | admin |
| PUT | `/users/<id>` | admin |
| DELETE | `/users/<id>` | admin |

### Productos

| Metodo | Ruta | Acceso |
|---|---|---|
| GET | `/products` | admin y cliente |
| GET | `/products/<id>` | admin y cliente |
| POST | `/products` | admin |
| PUT | `/products/<id>` | admin |
| DELETE | `/products/<id>` | admin |

### Carritos

| Metodo | Ruta | Acceso |
|---|---|---|
| GET | `/carts` | el cliente ve los suyos; el admin, todos |
| POST | `/carts` | admin y cliente |
| GET | `/carts/<id>` | el dueno o el admin |
| DELETE | `/carts/<id>` | el dueno o el admin |
| POST | `/carts/<id>/items` | el dueno o el admin |
| PUT | `/carts/<id>/items/<product_id>` | el dueno o el admin |
| DELETE | `/carts/<id>/items/<product_id>` | el dueno o el admin |

`POST /items` suma a la cantidad existente; `PUT /items/<product_id>` la
reemplaza.

### Ventas y facturas

| Metodo | Ruta | Acceso |
|---|---|---|
| POST | `/carts/<id>/checkout` | el dueno del carrito |
| GET | `/invoices` | el cliente ve las suyas; el admin, todas |
| GET | `/invoices/<invoice_number>` | el dueno o el admin |
| POST | `/invoices/<invoice_number>/refund` | admin |
| PUT | `/invoices/<invoice_number>` | admin |
| DELETE | `/invoices/<invoice_number>` | admin, solo si ya fue devuelta |

La venta se realiza sobre el carrito y no mediante un `POST /invoices` generico. El
cliente tiene que poder concretar una venta, pero la creacion y modificacion de
facturas esta reservada al admin; facturar el propio carrito satisface ambas
condiciones, porque los montos los calcula el servidor y no viajan en la peticion.

## Ejemplo: registrar una venta

```http
POST /carts/1/checkout
Authorization: Bearer <token del cliente>
Content-Type: application/json

{
  "billing_address": {
    "full_name": "Maria Rodriguez",
    "phone": "88887777",
    "province": "San Jose",
    "canton": "Escazu",
    "district": "San Rafael",
    "exact_address": "200 metros norte de la iglesia"
  },
  "payment": {
    "method": "sinpe",
    "sinpe_phone": "88887777",
    "sinpe_reference": "SINPE-0001"
  }
}
```

Responde `201` con el numero de factura (`INV-2026-000001`), las lineas con el
precio vigente al momento de la venta, la direccion de cobro y los datos del pago.

El checkout completo ocurre dentro de un unico `engine.begin()`. Si algun producto
no tiene stock suficiente, la transaccion se revierte por completo: no se emite
factura, no se descuenta inventario y el carrito permanece abierto para corregirlo.

## Cache

| Llave | Contenido | TTL | Se invalida al |
|---|---|---|---|
| `products:all` | catalogo de productos activos | 300 s | crear, editar o desactivar un producto, y tras una venta o devolucion |
| `product:<id>` | detalle de un producto | 300 s | igual que el anterior, acotado a ese producto |
| `invoice:<numero>` | factura completa | 600 s | procesar una devolucion, corregir la referencia SINPE o eliminarla |

Las facturas tienen un TTL mayor porque, una vez emitidas, practicamente no
cambian.

El inventario nunca se lee desde cache al vender: dentro de la transaccion se
consulta siempre PostgreSQL con `FOR UPDATE`. El cache acelera la lectura del
catalogo, pero no participa en ninguna decision de negocio.

## Roles y codigos de respuesta

| Rol | Alcance |
|---|---|
| `admin` | crear, editar y desactivar productos y usuarios; consultar todas las facturas; procesar devoluciones |
| `client` | consultar el catalogo, administrar sus carritos, facturar y consultar sus propias facturas |

| Codigo | Cuando se devuelve |
|---|---|
| `400` | datos invalidos o incompletos en la peticion |
| `401` | falta el token, es invalido, vencio, o el usuario fue desactivado |
| `403` | el rol no tiene permiso, o el recurso pertenece a otro usuario |
| `404` | el recurso no existe |
| `409` | conflicto de estado: usuario duplicado, carrito ya facturado, factura ya devuelta |

## Documentacion adicional

- [`docs/er-diagram.md`](docs/er-diagram.md): diagrama entidad-relacion,
  diccionario de datos, normalizacion y restricciones.
- [`docs/technical-decisions.md`](docs/technical-decisions.md): decisiones de
  diseno, su justificacion y las alternativas descartadas.

## Limitaciones conocidas

- **Hash de contrasenas con MD5.** No es apto para produccion: MD5 es rapido de
  romper y aqui se aplica sin salt. Un entorno real requiere `bcrypt` o `argon2`.
  El cambio esta acotado a la funcion `hash_password()` de `db.py`.
- **Sin migraciones.** El esquema se crea con `create_all()`, que solo agrega lo
  que falta y no altera tablas existentes. Modificar una columna obliga a recrear
  la tabla. Una herramienta como Alembic resolveria esto.
- **Sin paginacion.** Los listados devuelven todos los registros, lo que resulta
  suficiente para el volumen previsto pero no escala.
- **Devoluciones totales unicamente.** No se admiten devoluciones parciales por
  linea de factura.
