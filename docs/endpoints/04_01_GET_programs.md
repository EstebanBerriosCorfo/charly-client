# Endpoint: GET /programs

## Descripción

Lista todas las convocatorias (programs) disponibles. Permite filtrar por organización, estado de postulación, estado de evaluación y fecha de creación.

---

## Especificación Técnica

| Propiedad | Valor |
|-----------|-------|
| **Método HTTP** | `GET` |
| **Path** | `/programs` |
| **Requiere API Key** | ✅ Sí |
| **Paginado** | ✅ Sí |
| **Base URL** | `https://app.charly.io/api/v1` |

---

## Request

### Query Parameters

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `api_key` | `string` | ✅ Sí | API key obtenida de `/sessions` |
| `organization_id` | `integer` | ❌ No | Filtrar por organización |
| `application_status` | `string` | ❌ No | Estado: `draft`, `open`, `finished` |
| `evaluation_status` | `string` | ❌ No | Estado: `draft`, `open`, `finished` |
| `created_at` | `string` | ❌ No | Fecha mínima (YYYY-MM-DD) |
| `page` | `integer` | ❌ No | Número de página (paginación) |

### URL Completa

```
GET https://app.charly.io/api/v1/programs?api_key=abc123...&organization_id=123&application_status=open
```

---

## Response

### Status Code: 200 OK

**Formato Paginado:**

```json
{
    "count": 50,
    "previous": null,
    "next": "https://app.charly.io/api/v1/programs?page=2&organization_id=123",
    "results": [
        {
            "id": 1234,
            "name": "Convocatoria Innovación 2024",
            "organization_id": 123,
            "application_status": "open",
            "evaluation_status": "open",
            "description": "Convocatoria para proyectos de innovación",
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-12-31T23:59:59Z",
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-20T14:30:00Z"
        },
        {
            "id": 5678,
            "name": "Convocatoria I+D 2024",
            "organization_id": 123,
            "application_status": "finished",
            "evaluation_status": "finished",
            "description": "Convocatoria para proyectos I+D",
            "start_date": "2024-02-01T00:00:00Z",
            "end_date": "2024-11-30T23:59:59Z",
            "created_at": "2024-02-01T09:00:00Z",
            "updated_at": "2024-12-01T16:45:00Z"
        }
    ]
}
```

### Campos de Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `count` | `integer` | Total de convocatorias que coinciden con los filtros |
| `previous` | `string\|null` | URL de la página anterior |
| `next` | `string\|null` | URL de la página siguiente |
| `results` | `array` | Lista de convocatorias en la página actual |

### Campos de Program

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `integer` | ID único de la convocatoria |
| `name` | `string` | Nombre de la convocatoria |
| `organization_id` | `integer` | ID de la organización |
| `application_status` | `string` | Estado: `draft`, `open`, `finished` |
| `evaluation_status` | `string` | Estado: `draft`, `open`, `finished` |
| `description` | `string\|null` | Descripción de la convocatoria |
| `start_date` | `string\|null` | Fecha de inicio (ISO8601) |
| `end_date` | `string\|null` | Fecha de término (ISO8601) |
| `created_at` | `string` | Fecha de creación (ISO8601) |
| `updated_at` | `string` | Fecha de última actualización (ISO8601) |

---

## Ejemplo de Uso

### Usando ProgramService (Recomendado)

```python
from pathlib import Path
from orchestration.bootstrap import Bootstrap
from services.program_service import ProgramService

# Bootstrap
ctx = Bootstrap(config_path=Path("config/charly.yaml")).run()
client = ctx["client"]

# Listar convocatorias con filtros
program_service = ProgramService(client)
response = program_service.list_programs(
    organization_id=123,
    application_status="open",
    evaluation_status="open"
)

print(f"Total convocatorias: {response['count']}")
for program in response['results']:
    print(f"- {program['name']} (ID: {program['id']})")
```

### Iteración Completa (Todas las Páginas)

```python
program_service = ProgramService(client)

# Iterar todas las convocatorias automáticamente
for program in program_service.iterate_programs(
    organization_id=123,
    application_status="open"
):
    print(f"- {program['name']} (ID: {program['id']})")
```

### Sin Filtros (Todas las Convocatorias)

```python
# Sin filtros, obtiene todas las convocatorias accesibles
for program in program_service.iterate_programs():
    print(f"- {program['name']} (ID: {program['id']})")
```

### Request HTTP Directo

```python
import urllib.request
import urllib.parse

api_key = "tu_api_key_aqui"
base_url = "https://app.charly.io/api/v1"

params = urllib.parse.urlencode({
    "api_key": api_key,
    "organization_id": 123,
    "application_status": "open",
    "evaluation_status": "open"
})
url = f"{base_url}/programs?{params}"

request = urllib.request.Request(url=url, method="GET")

with urllib.request.urlopen(request, timeout=30) as response:
    import json
    data = json.loads(response.read().decode("utf-8"))
    
    print(f"Total: {data['count']}")
    for program in data['results']:
        print(f"- {program['name']}")
```

---

## Filtros Disponibles

### Por Organización

```python
# Solo convocatorias de una organización específica
programs = program_service.iterate_programs(organization_id=123)
```

### Por Estado de Postulación

```python
# Solo convocatorias abiertas para postulación
programs = program_service.iterate_programs(application_status="open")

# Solo convocatorias finalizadas
programs = program_service.iterate_programs(application_status="finished")

# Solo borradores
programs = program_service.iterate_programs(application_status="draft")
```

### Por Estado de Evaluación

```python
# Solo convocatorias con evaluación abierta
programs = program_service.iterate_programs(evaluation_status="open")

# Solo convocatorias con evaluación finalizada
programs = program_service.iterate_programs(evaluation_status="finished")
```

### Por Fecha de Creación

```python
# Convocatorias creadas desde una fecha específica
programs = program_service.iterate_programs(created_at="2024-01-01")
```

### Combinación de Filtros

```python
# Convocatorias abiertas de una organización específica
programs = program_service.iterate_programs(
    organization_id=123,
    application_status="open",
    evaluation_status="open",
    created_at="2024-01-01"
)
```

---

## Paginación

Este endpoint es paginado. El sistema maneja automáticamente la paginación:

```python
# Paginación automática
for program in program_service.iterate_programs(organization_id=123):
    process_program(program)
```

---

## Manejo de Errores

### 400 Bad Request

Parámetros inválidos (fecha mal formateada, estado inválido).

```json
{
    "error": "Invalid application_status"
}
```

### 401 Unauthorized

API key inválida o expirada.

### 403 Forbidden

Usuario no tiene permisos para listar convocatorias.

---

## Casos de Uso

### Caso 1: Listar Convocatorias Abiertas

```python
program_service = ProgramService(client)

open_programs = []
for program in program_service.iterate_programs(
    application_status="open"
):
    open_programs.append(program)

print(f"Convocatorias abiertas: {len(open_programs)}")
```

### Caso 2: Convocatorias por Organización

```python
program_service = ProgramService(client)

org_programs = {}
for program in program_service.iterate_programs():
    org_id = program['organization_id']
    if org_id not in org_programs:
        org_programs[org_id] = []
    org_programs[org_id].append(program)

for org_id, programs in org_programs.items():
    print(f"Org {org_id}: {len(programs)} convocatorias")
```

### Caso 3: Convocatorias Finalizadas con Evaluación

```python
program_service = ProgramService(client)

finished_programs = []
for program in program_service.iterate_programs(
    application_status="finished",
    evaluation_status="finished"
):
    finished_programs.append(program)

print(f"Convocatorias completamente finalizadas: {len(finished_programs)}")
```

---

## Script de Ejemplo

Ver `scripts/04_01_programs.py`:

```python
from orchestration.bootstrap import Bootstrap
from services.program_service import ProgramService

ctx = Bootstrap(config_path=Path("config/charly.yaml")).run()
client = ctx["client"]

program_service = ProgramService(client)

# Input de filtros
org_id = input("Organization ID (Enter para omitir): ").strip()
application_status = input("Application status [draft/open/finished]: ").strip()
evaluation_status = input("Evaluation status [draft/open/finished]: ").strip()
created_at = input("Created at desde (YYYY-MM-DD): ").strip()

filters = {}
if org_id:
    filters["organization_id"] = int(org_id)
if application_status:
    filters["application_status"] = application_status
if evaluation_status:
    filters["evaluation_status"] = evaluation_status
if created_at:
    filters["created_at"] = created_at

# Consulta
response = program_service.list_programs(**filters)
programs = response.get("results", [])

print("\n=== PROGRAMS / CONVOCATORIAS ===")
print(f"Total encontrados: {response.get('count', 0)}\n")

for program in programs:
    print(
        f"- ID: {program['id']} | "
        f"Nombre: {program['name']} | "
        f"Org: {program['organization_id']} | "
        f"Postulación: {program['application_status']} | "
        f"Evaluación: {program['evaluation_status']}"
    )
```

---

## Notas Importantes

1. **Filtros Opcionales:**
   - Todos los filtros son opcionales
   - Sin filtros, retorna todas las convocatorias accesibles

2. **Estados:**
   - `draft`: Borrador, no visible públicamente
   - `open`: Abierto para postulación/evaluación
   - `finished`: Finalizado

3. **Rendimiento:**
   - Usar filtros para reducir el volumen de datos
   - Siempre usar `iterate_programs()` para paginación automática

---

## Referencias

- **Implementación:** `services/program_service.py` - Clase `ProgramService`
- **Script:** `scripts/04_01_programs.py`
- **Orquestación:** `orchestration/extract_programs.py` - Clase `ProgramExtractor`
