# Publicación de WoodMetrics

Repositorio objetivo: https://github.com/martingaonauni03-boop/woodmetrics

## 1. Subir el proyecto

El proyecto debe estar en el repositorio con `requirements.txt`, `wsgi.py`, `woodmetrics/` y `render.yaml`. No subir `instance/`, `.env` ni `.deps/`.

## 2. Render con persistencia SQLite

El archivo `render.yaml` define un servicio Python con disco persistente. **Usa un plan de pago**: revisa el precio mostrado por Render antes de confirmar la creación. No se ha contratado ningún servicio como parte del código.

1. Inicia sesión en Render con tu cuenta.
2. Selecciona **New → Blueprint** y conecta el repositorio `woodmetrics`.
3. Revisa el servicio, el plan y el disco de 1 GB propuestos por el blueprint.
4. Confirma el despliegue si aceptas el coste mostrado.
5. El build instala `requirements.txt`; el arranque ejecuta `gunicorn --bind 0.0.0.0:$PORT --workers 1 wsgi:app`.
6. La variable `DATABASE_PATH` apunta a `/var/data/woodmetrics.sqlite`, dentro del disco. `SECRET_KEY` se genera en Render; no la copies al repositorio. `COOKIE_SECURE=1` requiere HTTPS.
7. Tras el primer despliegue abre la consola **Shell** del servicio y ejecuta:

```bash
python -m flask --app wsgi seed-demo
python -m flask --app wsgi create-admin
```

8. Elige tu correo y una contraseña propia cuando el comando lo solicite.
9. Abre la URL HTTPS del servicio e inicia sesión.
10. Crea un registro, reinicia el servicio y verifica que el registro permanece. Comprueba `/health` y la creación/edición de un pedido.

No uses una base SQLite en un servicio gratuito efímero como almacenamiento final: sus cambios se pierden cuando el servicio se reinicia o vuelve a desplegarse. Si el presupuesto debe ser cero, selecciona un alojamiento que permita guardar SQLite de forma persistente, o acuerda migrar la persistencia a una base externa. Esa decisión debe tomarse antes de publicar la entrega definitiva.

## 3. Alternativa: servidor con Docker y volumen

```bash
docker build -t woodmetrics .
docker volume create woodmetrics-data
docker run --name woodmetrics -p 8000:8000 --mount source=woodmetrics-data,target=/data -e SECRET_KEY -e COOKIE_SECURE=1 woodmetrics
```

El administrador del servidor debe definir `SECRET_KEY` en su entorno antes de ejecutar el comando, proporcionar HTTPS mediante un proxy y asegurar que el usuario del contenedor pueda escribir en el volumen. Con HTTP local usa `COOKIE_SECURE=0`.

Crear datos y administrador:

```bash
docker exec -it woodmetrics python -m flask --app wsgi seed-demo
docker exec -it woodmetrics python -m flask --app wsgi create-admin
```

## Evidencia de despliegue que debes entregar

- URL HTTPS que realmente funcione, no una URL de ejemplo.
- Inicio de sesión y guardado de un registro desde esa URL.
- Enlace del repositorio y commit utilizado.
- Enlace del video en Loom o YouTube, accesible para el docente.

## Fuentes oficiales consultadas

- Flask en Render: https://render.com/docs/deploy-flask
- Discos persistentes: https://render.com/docs/disks
- Limitaciones gratuitas: https://render.com/docs/free
- Referencia del blueprint: https://render.com/docs/blueprint-spec
