# Despliegue gratuito en PythonAnywhere

Alternativa para conservar Python, Flask y SQLite sin contratar el disco de Render. La cuenta gratuita admite una aplicación web y SQLite; tiene límites de recursos y requiere renovar la web desde el panel antes de su vencimiento (actualmente un mes). Revisa las condiciones mostradas al crear tu cuenta.

## 1. Cuenta y código

Crea una cuenta Beginner en https://www.pythonanywhere.com/ y abre una consola Bash. Sustituye `TU_USUARIO` por tu nombre de usuario real en todos los pasos.

```bash
git clone --branch codex/administracion-mvc https://github.com/martingaonauni03-boop/woodmetrics.git
cd woodmetrics
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdir -p instance
umask 077
python -c "import secrets; print(secrets.token_hex(32))" > instance/secret.key
python -m flask --app wsgi seed-demo
python -m flask --app wsgi create-admin
```

Si Python 3.12 no está disponible, usa una versión Python compatible con las dependencias que aparezca en el panel y selecciónala también al crear la web. El comando de administrador solicita tu correo y contraseña; no los incluyas en GitHub ni en el video.

## 2. Crear la web

En la pestaña **Web**, selecciona **Add a new web app → Manual configuration** y elige la misma versión de Python del entorno virtual.

Configura:

- **Source code:** `/home/TU_USUARIO/woodmetrics`
- **Working directory:** `/home/TU_USUARIO/woodmetrics`
- **Virtualenv:** `/home/TU_USUARIO/woodmetrics/.venv`

Abre el archivo WSGI mediante el enlace del panel Web y reemplaza su contenido por:

```python
import os
import sys
from pathlib import Path

project = Path('/home/TU_USUARIO/woodmetrics')
sys.path.insert(0, str(project))
os.environ['SECRET_KEY'] = (project / 'instance' / 'secret.key').read_text().strip()
os.environ['DATABASE_PATH'] = str(project / 'instance' / 'woodmetrics.sqlite')
os.environ['COOKIE_SECURE'] = '1'

from wsgi import app as application
```

No uses `app.run()` en ese archivo. Guarda y pulsa **Reload**. Utiliza la dirección **HTTPS** asignada por PythonAnywhere; con `COOKIE_SECURE=1` no podrás iniciar sesión mediante HTTP.

## 3. Verificar

1. Abre `https://TU_USUARIO.pythonanywhere.com/health`: debe responder `{"status":"ok"}`.
2. Inicia sesión y crea un cliente ficticio desde esa dirección.
3. Pulsa Reload en Web y comprueba que el cliente sigue guardado.
4. Demuestra los selectores dependientes y la validación del servidor.
5. Guarda la URL real para tu entrega. Revisa la fecha de expiración del servicio y renueva desde el panel cuando corresponda.

Para actualizar el código posteriormente, ejecuta `git pull` en la consola del proyecto y pulsa Reload. Haz copia de seguridad de `instance/` antes de cambios importantes. No vuelvas a generar `secret.key` en cada actualización.

## Fuentes oficiales

- Planes: https://www.pythonanywhere.com/pricing/
- Cuenta gratuita y vencimiento: https://help.pythonanywhere.com/pages/FreeAccountsFeatures/
- Bases de datos: https://help.pythonanywhere.com/pages/KindsOfDatabases/
- Configuración Flask/WSGI: https://help.pythonanywhere.com/pages/Flask/
