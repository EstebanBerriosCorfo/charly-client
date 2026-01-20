# Endpoint: GET /programs/{program_id}

## Descripción

Obtiene el detalle completo de una convocatoria específica, incluyendo **todas las postulaciones (applications)** asociadas. Este es uno de los endpoints más importantes para obtener datos completos de una convocatoria.

---

## Especificación Técnica

| Propiedad | Valor |
|-----------|-------|
| **Método HTTP** | `GET` |
| **Path** | `/programs/{program_id}` |
| **Requiere API Key** | ✅ Sí |
| **Paginado** | ❌ No |
| **Base URL** | `https://app.charly.io/api/v1` |

---

## Request

### Path Parameters

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `program_id` | `integer` | ✅ Sí | ID de la convocatoria |

### Query Parameters

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `api_key` | `string` | ✅ Sí | API key obtenida de `/sessions` |
| `company_application_status` | `string` | ❌ No | Filtrar postulaciones: `pending`, `complete`, `sent` |

### URL Completa

```
GET https://app.charly.io/api/v1/programs/1234?api_key=abc123...&company_application_status=sent
```

---

## Response

### Status Code: 200 OK

```json
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
    "updated_at": "2024-01-20T14:30:00Z",
    "applications": [
        {
            "id": 5678,
            "program_id": 1234,
            "name": "Postulación Empresa XYZ",
            "application_status": "sent",
            "company_application_status": "sent",
            "application_sent_at": "2024-02-15T14:30:00Z",
            "assigned_evaluators_count": 3,
            "form_answers_count": 5,
            "score_admin": 85.5,
            "score_algo": 90.0,
            "score_eval": 88.0,
            "company": {
                "id": 999,
                "name": "Empresa XYZ",
                "email": "contacto@xyz.com"
            }
        },
        {
            "id": 5679,
            "program_id": 1234,
            "name": "Postulación Empresa ABC",
            "application_status": "sent",
            "company_application_status": "sent",
            "application_sent_at": "2024-02-16T10:15:00Z",
            "assigned_evaluators_count": 2,
            "form_answers_count": 4,
            "score_admin": 92.0,
            "score_algo": 88.5,
            "score_eval": 90.0,
            "company": {
                "id": 1000,
                "name": "Empresa ABC",
                "email": "info@abc.com"
            }
        }
    ]
}
```

### Campos de Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `integer` | ID único de la convocatoria |
| `name` | `string` | Nombre de la convocatoria |
| `organization_id` | `integer` | ID de la organización |
| `application_status` | `string` | Estado de postulación |
| `evaluation_status` | `string` | Estado de evaluación |
| `description` | `string\|null` | Descripción |
| `start_date` | `string\|null` | Fecha de inicio |
| `end_date` | `string\|null` | Fecha de término |
| `created_at` | `string` | Fecha de creación |
| `updated_at` | `string` | Fecha de actualización |
| `applications` | `array` | **Lista completa de postulaciones** |

### Campos de Application (en applications array)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `integer` | ID de la postulación |
| `program_id` | `integer` | ID de la convocatoria |
| `name` | `string` | Nombre de la postulación |
| `application_status` | `string` | Estado de la postulación |
| `company_application_status` | `string` | Estado desde perspectiva empresa: `pending`, `complete`, `sent` |
| `application_sent_at` | `string\|null` | Fecha de envío |
| `assigned_evaluators_count` | `integer` | Número de evaluadores asignados |
| `form_answers_count` | `integer` | Número de formularios respondidos |
| `score_admin` | `float\|null` | Puntaje administrativo |
| `score_algo` | `float\|null` | Puntaje algorítmico |
| `score_eval` | `float\|null` | Puntaje de evaluación |
| `company` | `object` | Información de la empresa postulante |

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

# Obtener convocatoria con postulaciones
program_service = ProgramService(client)
program_detail = program_service.get_program(program_id=1234)

print(f"Convocatoria: {program_detail['name']}")
print(f"Total postulaciones: {len(program_detail.get('applications', []))}")

# Iterar postulaciones
for application in program_detail.get('applications', []):
    print(f"- {application['name']} (ID: {application['id']})")
```

### Con Filtro de Estado

```python
# Solo postulaciones enviadas
program_detail = program_service.get_program(
    program_id=1234,
    company_application_status="sent"
)

sent_applications = program_detail.get('applications', [])
print(f"Postulaciones enviadas: {len(sent_applications)}")
```

### Request HTTP Directo

```python
import urllib.request
import urllib.parse

api_key = "tu_api_key_aqui"
base_url = "https://app.charly.io/api/v1"
program_id = 1234

params = urllib.parse.urlencode({
    "api_key": api_key,
    "company_application_status": "sent"
})
url = f"{base_url}/programs/{program_id}?{params}"

request = urllib.request.Request(url=url, method="GET")

with urllib.request.urlopen(request, timeout=30) as response:
    import json
    program_detail = json.loads(response.read().decode("utf-8"))
    
    print(f"Convocatoria: {program_detail['name']}")
    print(f"Postulaciones: {len(program_detail.get('applications', []))}")
```

---

## Filtros Disponibles

### Por Estado de Postulación de Empresa

```python
# Solo postulaciones pendientes
program_detail = program_service.get_program(
    program_id=1234,
    company_application_status="pending"
)

# Solo postulaciones completas (pero no enviadas)
program_detail = program_service.get_program(
    program_id=1234,
    company_application_status="complete"
)

# Solo postulaciones enviadas
program_detail = program_service.get_program(
    program_id=1234,
    company_application_status="sent"
)
```

---

## Manejo de Errores

### 404 Not Found

Convocatoria no encontrada o usuario no tiene acceso.

```json
{
    "error": "Program not found"
}
```

**Ejemplo de manejo:**

```python
from core.exceptions import CharlyApiError

try:
    program_detail = program_service.get_program(program_id=9999)
except CharlyApiError as e:
    if e.status_code == 404:
        print("Convocatoria no encontrada")
    else:
        print(f"Error: {e.message}")
```

### 401 Unauthorized

API key inválida o expirada.

### 403 Forbidden

Usuario no tiene permisos para acceder a esta convocatoria.

---

## Casos de Uso

### Caso 1: Obtener Todas las Postulaciones de una Convocatoria

```python
program_service = ProgramService(client)

program_detail = program_service.get_program(program_id=1234)
applications = program_detail.get('applications', [])

print(f"Total postulaciones: {len(applications)}")
for app in applications:
    print(f"- {app['name']} (ID: {app['id']})")
```

### Caso 2: Analizar Puntajes de Evaluación

```python
program_detail = program_service.get_program(program_id=1234)

scores = []
for app in program_detail.get('applications', []):
    if app.get('score_eval') is not None:
        scores.append({
            'application_id': app['id'],
            'name': app['name'],
            'score_eval': app['score_eval'],
            'score_admin': app.get('score_admin'),
            'score_algo': app.get('score_algo')
        })

# Ordenar por puntaje
scores.sort(key=lambda x: x['score_eval'], reverse=True)

print("Top 5 postulaciones:")
for score in scores[:5]:
    print(f"- {score['name']}: {score['score_eval']}")
```

### Caso 3: Estadísticas de Postulaciones

```python
program_detail = program_service.get_program(program_id=1234)
applications = program_detail.get('applications', [])

stats = {
    'total': len(applications),
    'sent': len([a for a in applications if a.get('company_application_status') == 'sent']),
    'complete': len([a for a in applications if a.get('company_application_status') == 'complete']),
    'pending': len([a for a in applications if a.get('company_application_status') == 'pending']),
    'with_scores': len([a for a in applications if a.get('score_eval') is not None])
}

print(f"Total: {stats['total']}")
print(f"Enviadas: {stats['sent']}")
print(f"Completas: {stats['complete']}")
print(f"Pendientes: {stats['pending']}")
print(f"Con evaluación: {stats['with_scores']}")
```

---

## Script de Ejemplo

Ver `scripts/04_02_programs_by_id.py`:

```python
from orchestration.bootstrap import Bootstrap
from services.organization_service import OrganizationService
from services.program_service import ProgramService

ctx = Bootstrap(config_path=Path("config/charly.yaml")).run()
client = ctx["client"]

org_service = OrganizationService(client)
program_service = ProgramService(client)

# Listar organizaciones
organizations = org_service.list()
print("\n=== ORGANIZACIONES DISPONIBLES ===")
for org in organizations:
    print(f"- ID: {org['id']} | Nombre: {org['name']}")

organization_id = int(input("\nIngrese el ID de la organización: "))

# Listar programas
programs = list(program_service.iterate_programs(organization_id=organization_id))
print("\n=== PROGRAMAS DISPONIBLES ===")
for program in programs:
    print(f"- ID: {program['id']} | Nombre: {program['name']}")

program_id = int(input("\nIngrese el ID del programa a consultar: "))

# Obtener detalle
program_detail = program_service.get_program(program_id)

print("\n=== PROGRAMA (DETALLE) ===")
pprint({k: v for k, v in program_detail.items() if k != "applications"})

# Postulaciones
applications = program_detail.get("applications", [])
print("\n=== POSTULACIONES ===")
print(f"Total: {len(applications)}")
for app in applications:
    print(json.dumps(app, indent=2, ensure_ascii=False))
```

---

## Notas Importantes

1. **Endpoint Costoso:**
   - ⚠️ Este endpoint incluye TODAS las postulaciones en la respuesta
   - Para convocatorias grandes puede ser muy pesado
   - Considerar usar filtros para reducir el volumen

2. **Postulaciones Incluidas:**
   - Las postulaciones incluyen información básica
   - Para respuestas completas (form_answers), usar `GET /applications/{id}`

3. **Filtro company_application_status:**
   - `pending`: Postulación iniciada pero no completada
   - `complete`: Postulación completada pero no enviada
   - `sent`: Postulación enviada oficialmente

4. **Rendimiento:**
   - Para análisis masivos, considerar usar `GET /applications` con filtros
   - Este endpoint es ideal para obtener contexto completo de una convocatoria

---

## Comparación con Otros Endpoints

| Característica | `GET /programs/{id}` | `GET /applications` |
|----------------|---------------------|---------------------|
| **Metadata de programa** | ✅ Sí | ❌ No |
| **Lista de applications** | ✅ Sí (básica) | ✅ Sí (completa) |
| **Filtros temporales** | ❌ No | ✅ Sí |
| **Respuestas completas** | ❌ No | ✅ Sí (con include_data) |

---

## Referencias

- **Implementación:** `services/program_service.py` - Clase `ProgramService`
- **Script:** `scripts/04_02_programs_by_id.py`
- **Orquestación:** `orchestration/extract_programs.py` - Clase `ProgramExtractor`
