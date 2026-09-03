# Backend Grupo 3 — Análisis de Compras
**FastAPI + Oracle Database**

API REST que conecta con la base de datos Oracle del proyecto y expone los resultados de las consultas SQL para el dashboard interactivo (Chart.js / ApexCharts).

---

## Requisitos previos

- Python 3.11 o superior
- Acceso a la base de datos Oracle del curso (credenciales proporcionadas en clase)

---

## Instalación (primera vez)

```powershell
cd "C:\ruta\backend_Grupo3"

# Crear entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Configurar credenciales
copy .env.example .env
# Abrir .env y completar ORACLE_USER, ORACLE_PASSWORD, ORACLE_HOST, etc.
```

---

## Arrancar el servidor

```powershell
.\.venv\Scripts\Activate.ps1
python run.py
```

Servidor disponible en: `http://127.0.0.1:8000`  
Documentación interactiva: `http://127.0.0.1:8000/docs`

---

## Estructura del proyecto

```
backend_Grupo3/
├── .env                 ← credenciales (NO subir a git)
├── .env.example         ← plantilla de credenciales
├── requirements.txt     ← dependencias Python
├── run.py               ← punto de entrada
└── app/
    ├── main.py          ← FastAPI, CORS, ciclo de vida del pool
    ├── config.py        ← lee variables del .env
    ├── database.py      ← pool Oracle + fetch_all / fetch_one
    ├── routers/
    │   ├── __init__.py  ← registra los routers bajo /api
    │   ├── health.py    ← /health y /meta/tables
    │   └── clientes.py  ← EJEMPLO de endpoints
    ├── services/
    │   └── clientes.py  ← EJEMPLO de consultas SQL
    └── schemas/
        └── common.py    ← modelos de respuesta Pydantic
```

| Capa | Responsabilidad |
|------|----------------|
| `database.py` | Conexión Oracle y ejecución de SQL |
| `services/*.py` | Consultas SQL y construcción de la respuesta |
| `routers/*.py` | Endpoints REST (URLs) |
| `routers/__init__.py` | Registro de cada router en la app |

---

## Cómo agregar un nuevo dominio

Sigue exactamente el mismo patrón que `clientes`. Ejemplo para **tarjetas**:

### 1. Crear `app/services/tarjetas.py`

```python
from app.database import fetch_all

def marca_mas_usada():
    sql = """
        SELECT
            m.nombre_marca,
            COUNT(e.id_compra) AS num_compras
        FROM tbl_enc_compras e
        JOIN tbl_tarjetas t ON t.id_tarjeta = e.id_tarjeta
        JOIN tbl_marcas m   ON m.id_marca   = t.id_marca
        GROUP BY m.nombre_marca
        ORDER BY num_compras DESC
    """
    data = fetch_all(sql)
    return {
        "question": "¿Qué marca de tarjeta se usa más?",
        "interpretation": f"La marca líder es {data[0]['nombre_marca']}." if data else "",
        "unit": "compras",
        "source": "Oracle Database · esquema DBA_COMPRAS",
        "data": data,
    }
```

> **Regla importante:** el SQL dentro de `""" ... """` debe ser Oracle puro,
> sin `{variables}` de Python. Ese mismo texto se puede copiar y pegar
> directamente en SQL Developer para verificarlo.

### 2. Crear `app/routers/tarjetas.py`

```python
from fastapi import APIRouter
from app.services import tarjetas as svc

router = APIRouter()

@router.get("/marca-mas-usada")
def marca_mas_usada():
    return svc.marca_mas_usada()
```

### 3. Registrar el router en `app/routers/__init__.py`

```python
from app.routers import clientes, tarjetas

api_router = APIRouter(prefix="/api")
api_router.include_router(clientes.router, prefix="/clientes", tags=["clientes"])
api_router.include_router(tarjetas.router, prefix="/tarjetas", tags=["tarjetas"])
```

La URL quedará disponible en:  
`http://127.0.0.1:8000/api/tarjetas/marca-mas-usada`

### Lo que NO hay que tocar

`database.py`, `config.py` y `main.py` ya resuelven la conexión.
Solo modificarlos si hay un problema de configuración.

---

## Tablas del esquema Oracle

| Tabla | Contenido |
|-------|-----------|
| `TBL_CLIENTES` | Datos personales del cliente |
| `TBL_TARJETAS` | Tarjetas asociadas a clientes |
| `TBL_MARCAS` | Marcas de tarjeta (Visa, Mastercard, etc.) |
| `TBL_PRODUCTOS` | Catálogo de productos con precio sugerido |
| `TBL_CATEGORIAS` | Categorías de productos |
| `TBL_ENC_COMPRAS` | Encabezado de cada compra (fecha, cliente, tarjeta, total) |
| `TBL_DET_COMPRAS` | Detalle de cada compra (producto, cantidad, subtotal) |

Para ver las columnas de cualquier tabla sin salir de la API:

```
GET /meta/tables/TBL_CLIENTES
```

---

## Cómo hacer pruebas

### 1. Swagger (recomendado)
Abrir `http://127.0.0.1:8000/docs` → **Try it out** → **Execute**

### 2. Navegador directo
```
http://127.0.0.1:8000/health?check_db=true
http://127.0.0.1:8000/meta/tables
http://127.0.0.1:8000/api/clientes/top-monto
http://127.0.0.1:8000/api/clientes/sin-compras
http://127.0.0.1:8000/api/clientes/ranking
```

### 3. PowerShell
```powershell
Invoke-RestMethod "http://127.0.0.1:8000/api/clientes/top-monto" | ConvertTo-Json -Depth 5
```

### 4. SQL Developer
Copiar el texto de `sql = """ ... """` (sin las comillas triples) y ejecutarlo
con el mismo usuario Oracle. Debe devolver los mismos datos.

> Si algo falla, revisar la terminal donde corre `python run.py`.
> Los errores de Oracle aparecen ahí.

---

## Formato de respuesta

Todos los endpoints deben devolver este formato:

```json
{
  "question":       "¿Cuál es la pregunta de negocio?",
  "interpretation": "Qué significan los datos obtenidos",
  "unit":           "monto (Q) | compras | cantidad | %",
  "source":         "Oracle Database · esquema DBA_COMPRAS",
  "analyzed_at":    "2026-09-03T12:00:00+00:00",
  "data":           [ ... ]
}
```

---

## División de trabajo

| Dominio | Archivos a crear |
|---------|-----------------|
| Clientes *(ejemplo ya hecho)* | `services/clientes.py`, `routers/clientes.py` |
| Tarjetas | `services/tarjetas.py`, `routers/tarjetas.py` |
| Productos y categorías | `services/productos.py`, `routers/productos.py` |
| Tiempo y tendencias | `services/tiempo.py`, `routers/tiempo.py` |
| KPIs del dashboard | `services/kpis.py`, `routers/kpis.py` |

Después de crear cada par servicio + router, registrarlo en `app/routers/__init__.py`.

---

## Endpoints disponibles actualmente

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | `/` | Índice y enlaces útiles |
| GET | `/health` | Estado de la API |
| GET | `/health?check_db=true` | Estado + conexión Oracle |
| GET | `/meta/tables` | Lista de tablas del esquema |
| GET | `/meta/tables/{nombre}` | Columnas de una tabla |
| GET | `/api/clientes/top-monto` | Top 10 clientes por monto |
| GET | `/api/clientes/sin-compras` | Clientes sin compras |
| GET | `/api/clientes/ranking` | Ranking por monto (DENSE_RANK) |
