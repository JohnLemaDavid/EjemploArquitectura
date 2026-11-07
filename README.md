# Balance Social Service

Un primer servicio con FastAPI que expone un endpoint GET.

## Requisitos

- Python 3.10 o superior.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) para gestionar las dependencias y el entorno virtual.

## Ejecutar

Desde la carpeta del proyecto:

```bash
uv run fastapi dev
```

`uv` crea el entorno virtual e instala las dependencias automáticamente. El servidor de desarrollo se inicia en `http://127.0.0.1:8000` y se recarga al modificar el código. Detenlo con `Ctrl+C`.

Si prefieres usar Python y pip en lugar de uv:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
fastapi dev
```

## Probar el endpoint

```bash
curl http://127.0.0.1:8000/
```

Respuesta esperada:

```json
{"message":"Hola, mundo"}
```

También puedes probarlo desde la documentación interactiva en [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). La documentación alternativa está en [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc).

El endpoint está definido en `app/main.py`: `@app.get("/")` asocia la ruta `/` al método HTTP GET y FastAPI convierte el diccionario de respuesta en JSON.

## Conectar con SQL Server

La conexión utiliza SQLAlchemy, `pyodbc` y el [controlador ODBC 18 de Microsoft](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server). Instala ese controlador en tu sistema antes de conectarte. En macOS puedes comprobar los controladores instalados con `odbcinst -q -d`.

1. Si todavía no tienes un archivo `.env`, copia `.env.example` como `.env`.
2. Completa `SQL_SERVER_HOST`, `SQL_SERVER_PORT`, `SQL_SERVER_DATABASE`, `SQL_SERVER_USER` y `SQL_SERVER_PASSWORD` con los datos de tu servidor. El puerto habitual es `1433`.
3. Instala las dependencias actualizadas con `uv sync` o, si usas pip, `python -m pip install -e .` dentro del entorno virtual.
4. Comprueba la conexión con `uv run python check_database.py` o `python check_database.py` con el entorno virtual activado. La comprobación solo ejecuta `SELECT 1`.

También puedes consultar `GET /health/database` con la API en ejecución. Devuelve `true` y HTTP 200 si `SELECT 1` funciona; si la conexión falla, devuelve `false` y HTTP 503. Por ejemplo: `curl http://127.0.0.1:8000/health/database`.

Por defecto se exige una conexión cifrada y un certificado válido. Para un servidor local de desarrollo con certificado autofirmado puedes establecer `SQL_SERVER_TRUST_SERVER_CERTIFICATE=yes`; para producción utiliza un certificado confiable y conserva `no`. Las variables de entorno del sistema tienen prioridad sobre el archivo `.env`. No compartas ni subas `.env` al repositorio.

`app/db/session.py` mantiene un motor compartido con un grupo de conexiones y proporciona `get_session` para inyectar una sesión por solicitud mediante `Depends(get_session)`. La sesión se cierra al terminar la solicitud. Las operaciones de escritura deberán confirmar explícitamente sus cambios con `session.commit()`. La conexión real se abre cuando se usa por primera vez, por lo que el GET `/` sigue funcionando independientemente de la base de datos.

## Usuarios activos

`GET /usuarios/activos` consulta `SEGURIDAD.USUARIO` y devuelve los registros con `ACTIVO = 1`, ordenados por usuario. Cada elemento contiene `usuario` y `nombre`; no se consulta la clave. Por ejemplo: `curl http://127.0.0.1:8000/usuarios/activos`. El endpoint actualmente no requiere autenticación; configura el control de acceso antes de exponerlo fuera de un entorno confiable.
