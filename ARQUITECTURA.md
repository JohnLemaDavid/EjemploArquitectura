# Arquitectura y estructura para proyectos FastAPI

Esta guía describe la organización usada en DataSacCore y sirve como punto de partida para otras API en Python. La estructura se organiza por dominios y separa el contrato HTTP, las reglas de negocio y el acceso a datos. Cada proyecto puede omitir los componentes que no necesite.

## Arquitectura

```text
Cliente HTTP
    │
    ▼
Router ──► Dependencias y autenticación
    │               │
    └───────────────▼
                 Servicio
                    │
            ┌───────┴────────┐
            ▼                ▼
       Repositorio       Cliente externo
            │                │
            ▼                ▼
     SQL / Mongo / Redis   API / ETL
```

- **Router:** recibe la solicitud, declara parámetros, autenticación, modelos de entrada y salida, y códigos HTTP. Delega el trabajo al servicio; no realiza consultas ni concentra reglas de negocio.
- **Dependencias:** construyen y proporcionan servicios, repositorios, sesiones y clientes mediante la inyección de dependencias de FastAPI. También permiten sustituirlos por implementaciones de prueba.
- **Servicio:** valida reglas de negocio, coordina repositorios o clientes, transforma resultados y administra las transacciones que correspondan al caso de uso.
- **Repositorio:** encapsula consultas y operaciones de persistencia, y convierte los datos al formato que necesita el servicio. Evita incluir reglas de negocio.
- **Cliente externo:** encapsula la comunicación con una API o servicio como un ETL, incluidos su configuración y manejo de errores de comunicación.
- **Schemas:** definen y validan los datos que entran y salen de la API con Pydantic.
- **Modelos de persistencia:** representan tablas o vistas mediante SQLAlchemy; son distintos de los schemas HTTP y no abren conexiones ni contienen reglas de negocio.

Las flechas representan llamadas, no necesariamente importaciones directas: `dependencies.py` ensambla las implementaciones concretas y el servicio las recibe por constructor. La respuesta regresa por el mismo recorrido hasta el cliente.

## Estructura general

```text
proyecto/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── session.py
│   │   ├── mongo.py                 # Si se utiliza MongoDB
│   │   └── redis.py                 # Si se utiliza Redis
│   ├── models/
│   │   └── <dominio>/               # Modelos de persistencia SQLAlchemy
│   ├── modules/
│   │   ├── auth/                    # Autenticación
│   │   └── <dominio>/               # Funcionalidades de negocio
│   ├── repositories/                # Componentes compartidos o existentes
│   └── routers/
│       └── health.py                # Estado de la aplicación y sus servicios
├── tests/
│   └── test_<funcionalidad>.py
├── docs/
├── pyproject.toml
├── requirements.txt
├── requirements.prod.txt
├── Dockerfile
├── compose.yaml
└── README.md
```

| Ruta | Función |
| --- | --- |
| `app/main.py` | Punto de composición: crea la aplicación, configura middleware y ciclo de vida, y registra los routers principales. |
| `app/core/` | Centraliza configuración y lectura de variables de entorno. |
| `app/db/` | Centraliza infraestructura de persistencia: bases declarativas, sesiones SQL y clientes MongoDB o Redis. |
| `app/models/` | Agrupa los modelos SQLAlchemy por dominio o esquema de datos. |
| `app/modules/` | Agrupa los casos de uso, contratos y acceso a datos por dominio o funcionalidad. |
| `app/repositories/` | Ubicación para repositorios compartidos o código existente; para funcionalidades nuevas se prefieren los repositorios dentro de su módulo. |
| `app/routers/` | Contiene routers transversales, como el de comprobación de estado. |
| `tests/` | Contiene pruebas de servicios, repositorios y endpoints según corresponda. |
| `docs/` | Reúne documentación técnica y otros recursos de consulta del proyecto. |
| `pyproject.toml` | Define metadatos, dependencias y configuración de herramientas como FastAPI y pytest. |
| `requirements.txt` y `requirements.prod.txt` | Listan dependencias para los entornos correspondientes. |
| `Dockerfile` y `compose.yaml` | Definen la imagen y la configuración de ejecución del contenedor. |
| `README.md` | Explica cómo configurar, ejecutar y probar el proyecto. |
| `__init__.py` | Identifica y organiza paquetes Python; puede estar vacío. |

## Estructura de un módulo

```text
app/modules/<dominio>/
├── __init__.py
├── router.py
├── dependencies.py
├── schemas.py
├── service.py
├── domain.py                       # Opcional
├── constants.py                    # Opcional
├── etl_client.py                   # Opcional
└── repositories/
    ├── __init__.py
    ├── sql_<funcionalidad>_repository.py
    └── mongo_<funcionalidad>_repository.py  # Solo si se necesita
```

| Archivo | Función |
| --- | --- |
| `router.py` | Define rutas, parámetros, autenticación, respuestas y errores HTTP; llama al servicio. |
| `dependencies.py` | Ensambla e inyecta las dependencias reales del módulo. |
| `schemas.py` | Define los contratos de solicitud y respuesta con Pydantic. |
| `service.py` | Implementa las reglas y la orquestación de la funcionalidad. |
| `repositories/` | Contiene consultas y operaciones específicas de cada fuente de datos. |
| `domain.py` | Aloja conceptos o estructuras propias del dominio cuando aportan claridad. |
| `constants.py` | Reúne constantes específicas de la funcionalidad cuando son necesarias. |
| `etl_client.py` u otro cliente | Encapsula la comunicación con un servicio externo. |

Un dominio grande puede contener subpaquetes por funcionalidad. Un router agrupador incluye los routers de esos subpaquetes y el router del dominio se registra en `app/main.py`. No es necesario crear archivos vacíos para capas que el caso de uso no necesita.

## Ejemplo del recorrido de una solicitud

Para consultar un reporte protegido:

1. El cliente envía la solicitud con su token Bearer.
2. `router.py` valida el contrato HTTP y solicita el contexto de autenticación y el servicio mediante dependencias.
3. `dependencies.py` construye el servicio con los repositorios o clientes necesarios.
4. `service.py` valida las reglas del reporte y pide los datos a los repositorios.
5. Los repositorios consultan las fuentes correspondientes; el servicio combina y transforma los resultados.
6. El router devuelve la respuesta conforme al schema declarado.

## Infraestructura y seguridad

En DataSacCore, SQL Server se accede mediante SQLAlchemy: `get_db` proporciona una sesión de la base principal y `get_secondary_db`, una de la secundaria. Los modelos utilizan `Base` o `BaseSecundaria` desde `app.db.base`. Las consultas usan parámetros y joins explícitos; no se usan `relationship` en los modelos. MongoDB y Redis tienen sus clientes en `app/db/`, y los módulos usan repositorios específicos cuando los necesitan.

Los endpoints nuevos de DataSacCore usan autenticación Bearer con `get_current_auth_context`. Las comprobaciones de roles o permisos se agregan cuando el requerimiento las define. La configuración y los secretos se reciben mediante variables de entorno; no deben incluirse credenciales en el código ni en la documentación. En otros proyectos, adapta los proveedores de datos y la autenticación a sus requisitos.

## Cómo agregar una funcionalidad

1. Definir el dominio, las rutas, los contratos, las fuentes de datos y la autenticación requerida.
2. Si depende de SQL Server en DataSacCore, inspeccionar primero el esquema real con el MCP `datasac_sql` y elegir la sesión adecuada.
3. Crear el paquete del dominio o funcionalidad y únicamente las capas necesarias.
4. Implementar los repositorios con consultas parametrizadas y los clientes externos necesarios.
5. Implementar el servicio recibiendo sus dependencias por constructor.
6. Definir los schemas y ensamblar las dependencias de FastAPI.
7. Crear el router, incorporarlo al agrupador correspondiente y registrar el router principal en `app/main.py` cuando sea necesario.
8. Agregar pruebas del servicio y del endpoint, y ejecutar las pruebas relevantes.

## Pruebas

Las pruebas unitarias del servicio pueden usar repositorios y clientes falsos para verificar reglas y casos límite sin conexiones reales. Las pruebas del endpoint verifican el contrato HTTP, la autenticación y la integración de dependencias; las pruebas de integración comprueban la interacción con infraestructura cuando corresponda.

```bash
pytest tests/test_<funcionalidad>.py
# O toda la suite:
pytest
```
