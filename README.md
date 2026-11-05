# WoodMetrics

Administración del sistema de planificación de cortes de tableros.

Aplicación: https://marting003.pythonanywhere.com/

## Tecnologías

Python 3.12, Flask, SQLite, HTML, CSS, JavaScript y Jinja2.

## Funciones

- Inicio de sesión con roles de administrador y operador.
- Administración de usuarios, categorías, tipos de tablero y formatos.
- Registro de clientes, pedidos y piezas.
- Configuración del ancho de sierra y las medidas mínimas de sobrantes.
- Selectores de tipos de tablero filtrados por categoría.
- Validaciones en servidor de medidas, cantidades, contraseñas y relaciones.
- Estados del pedido: Borrador, Listo y Cancelado.

## Estructura MVC

- `woodmetrics/models.py`: base de datos y relaciones.
- `woodmetrics/controllers.py`: rutas, sesiones y permisos.
- `woodmetrics/services.py`: validaciones del negocio.
- `woodmetrics/templates/`: vistas.
- `woodmetrics/static/`: estilos y JavaScript.

## Instalación

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:SECRET_KEY = (.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))")
.\.venv\Scripts\python.exe -m flask --app wsgi seed-demo
.\.venv\Scripts\python.exe -m flask --app wsgi create-admin
.\.venv\Scripts\python.exe -m flask --app wsgi run
```

Abrir http://127.0.0.1:5000 e ingresar con la cuenta creada. `seed-demo` carga datos de ejemplo una sola vez. La base se guarda en `instance/woodmetrics.sqlite`.

## Validaciones

El servidor valida los datos antes de guardarlos en SQLite:

- Ancho de sierra: mayor que 0 y máximo 20 mm.
- Largo, ancho y mínimos reutilizables: mayores que 0 y máximo 10 000 mm.
- Espesor: mayor que 0 y máximo 100 mm.
- Cantidad: entero entre 1 y 1000.
- Piezas: deben caber en un formato habilitado de su tipo, considerando el permiso de giro.
- Contraseñas: entre 10 y 128 caracteres, almacenadas como hash.
- Relaciones: los registros deben existir y el tipo de tablero debe pertenecer a la categoría seleccionada.

Un pedido necesita piezas válidas para pasar a Listo. Al modificar sus piezas vuelve a Borrador y aumenta su versión. Los registros relacionados no se pueden eliminar mientras estén en uso.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Configuración del servidor

Entrada WSGI: `wsgi:app`.

| Variable | Uso |
| --- | --- |
| `SECRET_KEY` | Clave de sesión estable y aleatoria. |
| `DATABASE_PATH` | Ruta del archivo SQLite en almacenamiento persistente. |
| `COOKIE_SECURE` | `1` para HTTPS; `0` para ejecución local con HTTP. |

```bash
gunicorn --bind 0.0.0.0:8000 --workers 1 wsgi:app
```

La base de datos y las claves no se incluyen en Git.
