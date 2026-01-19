# Endpoint: GET /mgr/fields

## Descripción

Lista todos los KPIs (fields) disponibles para una organización específica. Los KPIs representan métricas, preguntas y campos de evaluación que se utilizan en las convocatorias.

---

## Especificación Técnica

| Propiedad | Valor |
|-----------|-------|
| **Método HTTP** | `GET` |
| **Path** | `/mgr/fields` |
| **Requiere API Key** | ✅ Sí |
| **Paginado** | ✅ Sí |
| **Base URL** | `https://app.charly.io/api/v1` |

---

## Request

### Query Parameters

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `api_key` | `string` | ✅ Sí | API key obtenida de `/sessions` |
| `organization_id` | `integer` | ✅ Sí | ID de la organización |
| `page` | `integer` | ❌ No | Número de página (paginación) |

### URL Completa

```
GET https://app.charly.io/api/v1/mgr/fields?api_key=abc123...&organization_id=123
```

---

## Response

### Status Code: 200 OK

**Formato Paginado:**

```json
{
    "count": 25,
    "previous": null,
    "next": "https://app.charly.io/api/v1/mgr/fields?page=2&organization_id=123",
    "results": [
        {
            "id": 4444,
            "organization_id": 123,
            "field_type": "text",
            "component_type": "input",
            "field_function": "kpi",
            "weight": 10,
            "question": "Nombre de la empresa",
            "description": "Campo para capturar el nombre de la empresa postulante",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-15T10:00:00Z"
        },
        {
            "id": 4445,
            "organization_id": 123,
            "field_type": "number",
            "component_type": "input",
            "field_function": "kpi",
            "weight": 15,
            "question": "Número de empleados",
            "description": "Cantidad de empleados de la empresa",
            "created_at": "2024-01-02T00:00:00Z",
            "updated_at": "2024-01-16T11:00:00Z"
        }
    ]
}
```

### Campos de Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `count` | `integer` | Total de KPIs en la organización |
| `previous` | `string\|null` | URL de la página anterior |
| `next` | `string\|null` | URL de la página siguiente |
| `results` | `array` | Lista de KPIs en la página actual |

### Campos de KPI (Field)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `integer` | ID único del KPI |
| `organization_id` | `integer` | ID de la organización |
| `field_type` | `string` | Tipo de dato: `text`, `number`, `boolean`, `date`, etc. |
| `component_type` | `string` | Componente UI: `input`, `textarea`, `select`, `checkbox`, etc. |
| `field_function` | `string` | Función: `kpi`, `question`, `evaluation`, etc. |
| `weight` | `integer\|null` | Peso del KPI en evaluaciones |
| `question` | `string` | Pregunta o etiqueta del campo |
| `description` | `string\|null` | Descripción detallada |
| `created_at` | `string` | Fecha de creación (ISO8601) |
| `updated_at` | `string` | Fecha de última actualización (ISO8601) |

---

## Ejemplo de Uso

### Usando KPIService (Recomendado)

```python
from pathlib import Path
from orchestration.bootstrap import Bootstrap
from services.kpi_service import KPIService

# Bootstrap
ctx = Bootstrap(config_path=Path("config/charly.yaml")).run()
client = ctx["client"]

# Listar KPIs de una organización
kpi_service = KPIService(client)
response = kpi_service.list_kpis(organization_id=123)

print(f"Total KPIs: {response['count']}")
for kpi in response['results']:
    print(f"- {kpi['question']} (ID: {kpi['id']})")
```

### Iteración Completa (Todas las Páginas)

```python
kpi_service = KPIService(client)

# Iterar todos los KPIs automáticamente
for kpi in kpi_service.iterate_kpis(organization_id=123):
    print(f"- {kpi['question']} (ID: {kpi['id']}, Tipo: {kpi['field_type']})")
```

### Request HTTP Directo

```python
import urllib.request
import urllib.parse

api_key = "tu_api_key_aqui"
base_url = "https://app.charly.io/api/v1"
organization_id = 123

params = urllib.parse.urlencode({
    "api_key": api_key,
    "organization_id": organization_id
})
url = f"{base_url}/mgr/fields?{params}"

request = urllib.request.Request(url=url, method="GET")

with urllib.request.urlopen(request, timeout=30) as response:
    import json
    data = json.loads(response.read().decode("utf-8"))
    
    print(f"Total: {data['count']}")
    for kpi in data['results']:
        print(f"- {kpi['question']}")
```

---

## Paginación

Este endpoint es paginado. El sistema maneja automáticamente la paginación:

```python
# Paginación automática
for kpi in kpi_service.iterate_kpis(organization_id=123):
    process_kpi(kpi)
```

---

## Manejo de Errores

### 400 Bad Request

`organization_id` faltante o inválido.

```json
{
    "error": "organization_id is required"
}
```

### 401 Unauthorized

API key inválida o expirada.

### 403 Forbidden

Usuario no tiene permisos para acceder a esta organización.

### 404 Not Found

Organización no encontrada.

---

## Casos de Uso

### Caso 1: Listar Todos los KPIs de una Organización

```python
kpi_service = KPIService(client)

kpis = []
for kpi in kpi_service.iterate_kpis(organization_id=123):
    kpis.append(kpi)

print(f"Total KPIs: {len(kpis)}")
for kpi in kpis:
    print(f"- {kpi['question']} (Peso: {kpi.get('weight', 'N/A')})")
```

### Caso 2: Filtrar KPIs por Tipo

```python
kpi_service = KPIService(client)

text_kpis = []
number_kpis = []

for kpi in kpi_service.iterate_kpis(organization_id=123):
    if kpi['field_type'] == 'text':
        text_kpis.append(kpi)
    elif kpi['field_type'] == 'number':
        number_kpis.append(kpi)

print(f"KPIs de texto: {len(text_kpis)}")
print(f"KPIs numéricos: {len(number_kpis)}")
```

### Caso 3: Buscar KPI por Pregunta

```python
kpi_service = KPIService(client)

target_question = "Nombre de la empresa"
for kpi in kpi_service.iterate_kpis(organization_id=123):
    if kpi['question'] == target_question:
        print(f"KPI encontrado: {kpi['question']} (ID: {kpi['id']})")
        print(f"Tipo: {kpi['field_type']}, Componente: {kpi['component_type']}")
        break
```

### Caso 4: Extracción Masiva con Normalización

```python
from analytics.kpi_normalizer import KPINormalizer

kpi_service = KPIService(client)
normalizer = KPINormalizer()

all_kpi_metadata = []
all_kpi_data = []

for kpi in kpi_service.iterate_kpis(organization_id=123):
    # Obtener KPI completo con data agregada
    kpi_full = kpi_service.get_kpi(
        field_id=kpi['id'],
        organization_id=123
    )
    
    # Normalizar
    normalized = normalizer.normalize_kpi_full(kpi_full)
    all_kpi_metadata.extend(normalized["kpi_metadata"])
    all_kpi_data.extend(normalized["kpi_data"])

print(f"Total metadata: {len(all_kpi_metadata)}")
print(f"Total data: {len(all_kpi_data)}")
```

---

## Script de Ejemplo

Ver `scripts/06_kpis.py`:

```python
from orchestration.bootstrap import Bootstrap
from services.organization_service import OrganizationService
from services.kpi_service import KPIService

ctx = Bootstrap(config_path=Path("config/charly.yaml")).run()
client = ctx["client"]

org_service = OrganizationService(client)
kpi_service = KPIService(client)

# Seleccionar organización
org_id = org_service.list()[0]["id"]

# Listar KPIs
kpis = kpi_service.list_kpis(organization_id=org_id)

print(f"\n=== KPIs (ORG {org_id}) ===")
pprint(kpis)
```

---

## Notas Importantes

1. **organization_id Requerido:**
   - Este parámetro es SIEMPRE requerido
   - Los KPIs están asociados a organizaciones específicas

2. **Metadata vs Data:**
   - Este endpoint retorna solo metadata de los KPIs
   - Para obtener data agregada, usar `GET /mgr/fields/{field_id}`

3. **Tipos de Campos:**
   - `field_type`: Tipo de dato almacenado
   - `component_type`: Componente de UI usado para capturar
   - `field_function`: Función del campo (kpi, question, evaluation)

4. **Rendimiento:**
   - Usar `iterate_kpis()` para paginación automática
   - Para data agregada, necesitarás llamar `get_kpi()` por cada KPI

---

## Referencias

- **Implementación:** `services/kpi_service.py` - Clase `KPIService`
- **Normalización:** `analytics/kpi_normalizer.py` - Clase `KPINormalizer`
- **Orquestación:** `orchestration/extract_kpis.py` - Clase `KPIExtractor`
- **Script:** `scripts/06_kpis.py`
