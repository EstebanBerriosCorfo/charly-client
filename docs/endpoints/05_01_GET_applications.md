# Endpoint: GET /applications

## Descripción

Lista todas las postulaciones (applications) disponibles, con filtros por rango de fechas, IDs específicos y opción de incluir datos completos (respuestas y evaluaciones).

**⚠️ IMPORTANTE:** El parámetro `include_data=true` es costoso y puede hacer el request muy lento para grandes volúmenes.

---

## Especificación Técnica

| Propiedad | Valor |
|-----------|-------|
| **Método HTTP** | `GET` |
| **Path** | `/applications` |
| **Requiere API Key** | ✅ Sí |
| **Paginado** | ✅ Sí |
| **Base URL** | `https://app.charly.io/api/v1` |

---

## Request

### Query Parameters

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `api_key` | `string` | ✅ Sí | API key obtenida de `/sessions` |
| `start_date` | `string` | ❌ No | Fecha mínima (ISO8601, YYYY-MM-DD) |
| `end_date` | `string` | ❌ No | Fecha máxima (ISO8601, YYYY-MM-DD) |
| `date_type` | `string` | ❌ No | Tipo de fecha: `created_at` (default) o `updated_at` |
| `ids` | `string` | ❌ No | Lista de IDs separados por coma (ej: "123,456,789") |
| `include_data` | `string` | ❌ No | `"true"` para incluir respuestas y evaluaciones (costoso) |
| `page` | `integer` | ❌ No | Número de página (paginación) |

### URL Completa

```
GET https://app.charly.io/api/v1/applications?api_key=abc123...&start_date=2024-01-01&end_date=2024-12-31&date_type=created_at
```

---

## Response

### Status Code: 200 OK

**Formato Paginado (sin include_data):**

```json
{
    "count": 200,
    "previous": null,
    "next": "https://app.charly.io/api/v1/applications?page=2",
    "results": [
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
            },
            "created_at": "2024-02-10T10:00:00Z",
            "updated_at": "2024-02-15T14:30:00Z"
        }
    ]
}
```

**Con include_data=true (incluye respuestas completas):**

```json
{
    "count": 200,
    "results": [
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
            },
            "form_answers": [
                {
                    "id": 1111,
                    "form_id": 2222,
                    "answered_at": "2024-02-15T14:30:00Z",
                    "form": {
                        "id": 2222,
                        "name": "Formulario Principal",
                        "title": "Datos de la Empresa"
                    },
                    "field_answers": [
                        {
                            "id": 3333,
                            "answer": "Respuesta del campo",
                            "field": {
                                "id": 4444,
                                "name": "field_empresa_nombre",
                                "question": "Nombre de la empresa",
                                "field_type": "text",
                                "component_type": "input"
                            }
                        }
                    ]
                }
            ],
            "created_at": "2024-02-10T10:00:00Z",
            "updated_at": "2024-02-15T14:30:00Z"
        }
    ]
}
```

### Campos de Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `count` | `integer` | Total de postulaciones que coinciden con los filtros |
| `previous` | `string\|null` | URL de la página anterior |
| `next` | `string\|null` | URL de la página siguiente |
| `results` | `array` | Lista de postulaciones en la página actual |

### Campos de Application

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `integer` | ID único de la postulación |
| `program_id` | `integer` | ID de la convocatoria |
| `name` | `string` | Nombre de la postulación |
| `application_status` | `string` | Estado de la postulación |
| `company_application_status` | `string` | Estado desde perspectiva empresa |
| `application_sent_at` | `string\|null` | Fecha de envío |
| `assigned_evaluators_count` | `integer` | Número de evaluadores asignados |
| `form_answers_count` | `integer` | Número de formularios respondidos |
| `score_admin` | `float\|null` | Puntaje administrativo |
| `score_algo` | `float\|null` | Puntaje algorítmico |
| `score_eval` | `float\|null` | Puntaje de evaluación |
| `company` | `object` | Información de la empresa |
| `form_answers` | `array\|null` | Respuestas completas (solo con include_data=true) |
| `created_at` | `string` | Fecha de creación |
| `updated_at` | `string` | Fecha de actualización |

---

## Ejemplo de Uso

### Usando ApplicationService (Recomendado)

```python
from pathlib import Path
from orchestration.bootstrap import Bootstrap
from services.application_service import ApplicationService

# Bootstrap
ctx = Bootstrap(config_path=Path("config/charly.yaml")).run()
client = ctx["client"]

# Listar postulaciones con filtros temporales
application_service = ApplicationService(client)
response = application_service.list_applications(
    start_date="2024-01-01",
    end_date="2024-12-31",
    date_type="created_at",
    include_data=False  # Solo metadata
)

print(f"Total postulaciones: {response['count']}")
for app in response['results']:
    print(f"- {app['name']} (ID: {app['id']})")
```

### Iteración Completa (Todas las Páginas)

```python
application_service = ApplicationService(client)

# Iterar todas las postulaciones automáticamente
for application in application_service.iterate_applications(
    start_date="2024-01-01",
    end_date="2024-12-31",
    date_type="created_at",
    include_data=False
):
    print(f"- {application['name']} (ID: {application['id']})")
```

### Con Datos Completos (Costoso)

```python
# ⚠️ ADVERTENCIA: Esto puede ser muy lento para grandes volúmenes
application_service = ApplicationService(client)

for application in application_service.iterate_applications(
    start_date="2024-01-01",
    end_date="2024-01-31",  # Período corto recomendado
    include_data=True  # Incluye form_answers y field_answers
):
    # Procesar respuestas completas
    for form_answer in application.get('form_answers', []):
        print(f"Formulario: {form_answer['form']['name']}")
```

### Filtrar por IDs Específicos

```python
application_service = ApplicationService(client)

# Listar postulaciones específicas
response = application_service.list_applications(
    ids=[5678, 5679, 5680],
    include_data=False
)

for app in response['results']:
    print(f"- {app['name']} (ID: {app['id']})")
```

### Request HTTP Directo

```python
import urllib.request
import urllib.parse

api_key = "tu_api_key_aqui"
base_url = "https://app.charly.io/api/v1"

params = urllib.parse.urlencode({
    "api_key": api_key,
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "date_type": "created_at"
})
url = f"{base_url}/applications?{params}"

request = urllib.request.Request(url=url, method="GET")

with urllib.request.urlopen(request, timeout=30) as response:
    import json
    data = json.loads(response.read().decode("utf-8"))
    
    print(f"Total: {data['count']}")
    for app in data['results']:
        print(f"- {app['name']}")
```

---

## Filtros Disponibles

### Por Rango de Fechas

```python
# Postulaciones creadas en un período
applications = application_service.iterate_applications(
    start_date="2024-01-01",
    end_date="2024-12-31",
    date_type="created_at"
)

# Postulaciones actualizadas en un período
applications = application_service.iterate_applications(
    start_date="2024-02-01",
    end_date="2024-02-28",
    date_type="updated_at"
)
```

### Por IDs Específicos

```python
# Solo postulaciones específicas
response = application_service.list_applications(
    ids=[5678, 5679, 5680]
)
```

### Con Datos Completos

```python
# Incluir respuestas y evaluaciones (costoso)
applications = application_service.iterate_applications(
    start_date="2024-01-01",
    end_date="2024-01-31",  # Período corto recomendado
    include_data=True
)
```

---

## Paginación

Este endpoint es paginado. El sistema maneja automáticamente la paginación:

```python
# Paginación automática
for application in application_service.iterate_applications(
    start_date="2024-01-01",
    end_date="2024-12-31"
):
    process_application(application)
```

---

## Manejo de Errores

### 400 Bad Request

Parámetros inválidos (fechas mal formateadas, IDs inválidos).

```json
{
    "error": "Invalid date format"
}
```

### 401 Unauthorized

API key inválida o expirada.

### 403 Forbidden

Usuario no tiene permisos para listar postulaciones.

---

## Casos de Uso

### Caso 1: Postulaciones de un Período

```python
application_service = ApplicationService(client)

applications = []
for app in application_service.iterate_applications(
    start_date="2024-01-01",
    end_date="2024-12-31",
    date_type="created_at"
):
    applications.append(app)

print(f"Total postulaciones en 2024: {len(applications)}")
```

### Caso 2: Postulaciones Actualizadas Recientemente

```python
from datetime import datetime, timedelta

# Últimos 30 días
end_date = datetime.now().strftime("%Y-%m-%d")
start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

application_service = ApplicationService(client)

recent_apps = []
for app in application_service.iterate_applications(
    start_date=start_date,
    end_date=end_date,
    date_type="updated_at"
):
    recent_apps.append(app)

print(f"Postulaciones actualizadas recientemente: {len(recent_apps)}")
```

### Caso 3: Extracción Masiva con Normalización

```python
from analytics.application_normalizer import ApplicationNormalizer

application_service = ApplicationService(client)
normalizer = ApplicationNormalizer()

all_applications = []
all_form_answers = []
all_field_answers = []

for application in application_service.iterate_applications(
    start_date="2024-01-01",
    end_date="2024-12-31",
    include_data=True  # Necesario para normalización
):
    normalized = normalizer.normalize_application_full(application)
    all_applications.extend(normalized["applications"])
    all_form_answers.extend(normalized["form_answers"])
    all_field_answers.extend(normalized["field_answers"])

print(f"Total aplicaciones normalizadas: {len(all_applications)}")
print(f"Total respuestas de formularios: {len(all_form_answers)}")
print(f"Total respuestas de campos: {len(all_field_answers)}")
```

---

## Notas Importantes

1. **include_data=true es Costoso:**
   - ⚠️ Incluye todas las respuestas (form_answers y field_answers)
   - Puede hacer el request muy lento para grandes volúmenes
   - Usar solo cuando necesites las respuestas completas
   - Para análisis masivos, considerar usar `GET /applications/{id}` individualmente

2. **Filtros Temporales:**
   - Siempre usar filtros de fecha para limitar el volumen
   - `date_type` permite filtrar por creación o actualización

3. **Rendimiento:**
   - Para metadata básica, usar `include_data=False` (default)
   - Para respuestas completas, usar períodos cortos o IDs específicos

4. **Alternativa:**
   - Para obtener postulaciones de una convocatoria específica, usar `GET /programs/{id}`

---

## Comparación con Otros Endpoints

| Característica | `GET /applications` | `GET /programs/{id}` | `GET /applications/{id}` |
|----------------|---------------------|---------------------|------------------------|
| **Filtros temporales** | ✅ Sí | ❌ No | ❌ No |
| **Filtros por IDs** | ✅ Sí | ❌ No | ❌ No |
| **Metadata básica** | ✅ Sí | ✅ Sí | ✅ Sí |
| **Respuestas completas** | ✅ Sí (con include_data) | ❌ No | ✅ Sí |
| **Por convocatoria** | ❌ No | ✅ Sí | ❌ No |

---

## Referencias

- **Implementación:** `services/application_service.py` - Clase `ApplicationService`
- **Normalización:** `analytics/application_normalizer.py` - Clase `ApplicationNormalizer`
- **Orquestación:** `orchestration/extract_programs.py` - Clase `ProgramExtractor`
