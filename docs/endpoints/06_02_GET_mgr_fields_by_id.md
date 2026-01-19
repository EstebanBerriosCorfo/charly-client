# Endpoint: GET /mgr/fields/{field_id}

## Descripción

Obtiene el detalle completo de un KPI específico, incluyendo su **data agregada** (métricas, series temporales, distribuciones). Este endpoint es esencial para análisis de KPIs y métricas de evaluación.

---

## Especificación Técnica

| Propiedad | Valor |
|-----------|-------|
| **Método HTTP** | `GET` |
| **Path** | `/mgr/fields/{field_id}` |
| **Requiere API Key** | ✅ Sí |
| **Paginado** | ❌ No |
| **Base URL** | `https://app.charly.io/api/v1` |

---

## Request

### Path Parameters

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `field_id` | `integer` | ✅ Sí | ID del KPI (field) |

### Query Parameters

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `api_key` | `string` | ✅ Sí | API key obtenida de `/sessions` |
| `organization_id` | `integer` | ✅ Sí | ID de la organización |

### URL Completa

```
GET https://app.charly.io/api/v1/mgr/fields/4444?api_key=abc123...&organization_id=123
```

---

## Response

### Status Code: 200 OK

```json
{
    "id": 4444,
    "organization_id": 123,
    "field_type": "number",
    "component_type": "input",
    "field_function": "kpi",
    "weight": 15,
    "question": "Número de empleados",
    "description": "Cantidad de empleados de la empresa",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z",
    "data": {
        "labels": [
            "Enero 2024",
            "Febrero 2024",
            "Marzo 2024",
            "Abril 2024"
        ],
        "datasets": [
            {
                "label": "Promedio de empleados",
                "data": [5.2, 6.1, 7.3, 8.0]
            },
            {
                "label": "Mediana de empleados",
                "data": [4, 5, 6, 7]
            }
        ]
    }
}
```

### Campos de Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `integer` | ID único del KPI |
| `organization_id` | `integer` | ID de la organización |
| `field_type` | `string` | Tipo de dato |
| `component_type` | `string` | Componente UI |
| `field_function` | `string` | Función del campo |
| `weight` | `integer\|null` | Peso del KPI |
| `question` | `string` | Pregunta o etiqueta |
| `description` | `string\|null` | Descripción |
| `created_at` | `string` | Fecha de creación |
| `updated_at` | `string` | Fecha de actualización |
| `data` | `object\|null` | **Data agregada del KPI** |

### Estructura de data

El campo `data` contiene información agregada en formato compatible con gráficos:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `labels` | `array` | Etiquetas del eje X (categorías, fechas, etc.) |
| `datasets` | `array` | Series de datos, cada una con: |
| `datasets[].label` | `string` | Nombre de la serie |
| `datasets[].data` | `array` | Valores de la serie (alineados con labels) |

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

# Obtener KPI completo con data agregada
kpi_service = KPIService(client)
kpi_detail = kpi_service.get_kpi(
    field_id=4444,
    organization_id=123
)

print(f"KPI: {kpi_detail['question']}")
print(f"Tipo: {kpi_detail['field_type']}")
print(f"Peso: {kpi_detail.get('weight', 'N/A')}")

# Acceder a data agregada
if kpi_detail.get('data'):
    labels = kpi_detail['data'].get('labels', [])
    datasets = kpi_detail['data'].get('datasets', [])
    
    print(f"\nLabels: {labels}")
    for dataset in datasets:
        print(f"Serie '{dataset['label']}': {dataset['data']}")
```

### Normalización para BI

```python
from analytics.kpi_normalizer import KPINormalizer

kpi_service = KPIService(client)
normalizer = KPINormalizer()

# Obtener KPI completo
kpi_detail = kpi_service.get_kpi(
    field_id=4444,
    organization_id=123
)

# Normalizar en tablas planas
normalized = normalizer.normalize_kpi_full(kpi_detail)

# Tablas listas para BI/Excel
kpi_metadata = normalized["kpi_metadata"]  # 1 fila
kpi_data = normalized["kpi_data"]  # N filas (una por label × dataset)

print(f"Metadata: {len(kpi_metadata)} fila(s)")
print(f"Data: {len(kpi_data)} fila(s)")
```

### Extracción Masiva de KPIs

```python
from analytics.kpi_normalizer import KPINormalizer

kpi_service = KPIService(client)
normalizer = KPINormalizer()

all_metadata = []
all_data = []

# Iterar todos los KPIs
for kpi in kpi_service.iterate_kpis(organization_id=123):
    field_id = kpi['id']
    
    # Obtener KPI completo con data
    kpi_full = kpi_service.get_kpi(
        field_id=field_id,
        organization_id=123
    )
    
    # Normalizar
    normalized = normalizer.normalize_kpi_full(kpi_full)
    all_metadata.extend(normalized["kpi_metadata"])
    all_data.extend(normalized["kpi_data"])

print(f"Total KPIs procesados: {len(all_metadata)}")
print(f"Total filas de data: {len(all_data)}")
```

### Request HTTP Directo

```python
import urllib.request
import urllib.parse

api_key = "tu_api_key_aqui"
base_url = "https://app.charly.io/api/v1"
field_id = 4444
organization_id = 123

params = urllib.parse.urlencode({
    "api_key": api_key,
    "organization_id": organization_id
})
url = f"{base_url}/mgr/fields/{field_id}?{params}"

request = urllib.request.Request(url=url, method="GET")

with urllib.request.urlopen(request, timeout=30) as response:
    import json
    kpi_detail = json.loads(response.read().decode("utf-8"))
    
    print(f"KPI: {kpi_detail['question']}")
    if kpi_detail.get('data'):
        print(f"Data disponible: {len(kpi_detail['data'].get('datasets', []))} series")
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

### 404 Not Found

KPI no encontrado o no pertenece a la organización especificada.

```json
{
    "error": "Field not found"
}
```

**Ejemplo de manejo:**

```python
from core.exceptions import CharlyApiError

try:
    kpi_detail = kpi_service.get_kpi(
        field_id=9999,
        organization_id=123
    )
except CharlyApiError as e:
    if e.status_code == 404:
        print("KPI no encontrado o no pertenece a la organización")
    else:
        print(f"Error: {e.message}")
```

### 401 Unauthorized

API key inválida o expirada.

### 403 Forbidden

Usuario no tiene permisos para acceder a este KPI.

---

## Casos de Uso

### Caso 1: Análisis de Data Agregada

```python
kpi_service = KPIService(client)

kpi_detail = kpi_service.get_kpi(
    field_id=4444,
    organization_id=123
)

if kpi_detail.get('data'):
    data = kpi_detail['data']
    labels = data.get('labels', [])
    datasets = data.get('datasets', [])
    
    print(f"KPI: {kpi_detail['question']}")
    print(f"Períodos: {len(labels)}")
    
    for dataset in datasets:
        print(f"\nSerie: {dataset['label']}")
        print(f"Valores: {dataset['data']}")
        if dataset['data']:
            avg = sum(dataset['data']) / len(dataset['data'])
            print(f"Promedio: {avg:.2f}")
```

### Caso 2: Exportación a Excel

```python
from analytics.kpi_normalizer import KPINormalizer
import pandas as pd

kpi_service = KPIService(client)
normalizer = KPINormalizer()

kpi_detail = kpi_service.get_kpi(
    field_id=4444,
    organization_id=123
)

normalized = normalizer.normalize_kpi_full(kpi_detail)

# Crear DataFrames
df_metadata = pd.DataFrame(normalized["kpi_metadata"])
df_data = pd.DataFrame(normalized["kpi_data"])

# Exportar a Excel
with pd.ExcelWriter("kpi_4444.xlsx") as writer:
    df_metadata.to_excel(writer, sheet_name="Metadata", index=False)
    df_data.to_excel(writer, sheet_name="Data", index=False)
```

### Caso 3: Comparación de KPIs

```python
kpi_service = KPIService(client)

# Obtener múltiples KPIs
kpi1 = kpi_service.get_kpi(field_id=4444, organization_id=123)
kpi2 = kpi_service.get_kpi(field_id=4445, organization_id=123)

# Comparar pesos
weight1 = kpi1.get('weight', 0)
weight2 = kpi2.get('weight', 0)

print(f"{kpi1['question']}: peso {weight1}")
print(f"{kpi2['question']}: peso {weight2}")

if weight1 > weight2:
    print(f"{kpi1['question']} tiene mayor peso")
```

---

## Normalización de Datos

Este endpoint es ideal para normalización usando `KPINormalizer`:

### Tablas Generadas

1. **kpi_metadata_table** (1 fila por KPI)
   - Metadata: ID, organización, tipo, peso, pregunta, descripción

2. **kpi_data_table** (N filas, una por label × dataset)
   - Data agregada: field_id, organization_id, label, dataset_label, value

### Ejemplo de Normalización

```python
from analytics.kpi_normalizer import KPINormalizer

normalizer = KPINormalizer()
kpi_detail = kpi_service.get_kpi(field_id=4444, organization_id=123)

normalized = normalizer.normalize_kpi_full(kpi_detail)

# Estructura normalizada lista para BI
print(normalized.keys())
# dict_keys(['kpi_metadata', 'kpi_data'])

# Ejemplo de kpi_data:
# [
#     {'field_id': 4444, 'organization_id': 123, 'label': 'Enero 2024', 'dataset_label': 'Promedio', 'value': 5.2},
#     {'field_id': 4444, 'organization_id': 123, 'label': 'Febrero 2024', 'dataset_label': 'Promedio', 'value': 6.1},
#     ...
# ]
```

---

## Notas Importantes

1. **organization_id Requerido:**
   - Este parámetro es SIEMPRE requerido
   - El KPI debe pertenecer a la organización especificada

2. **Data Agregada:**
   - El campo `data` puede ser `null` si el KPI no tiene data agregada aún
   - La estructura sigue formato Chart.js (labels + datasets)

3. **Rendimiento:**
   - Este endpoint puede ser costoso si el KPI tiene mucha data
   - Para extracción masiva, considerar procesar en lotes

4. **Normalización:**
   - Siempre usar `KPINormalizer` para convertir a tablas planas
   - Facilita análisis en Excel, Power BI, SQL, etc.

---

## Comparación con Listado

| Característica | `GET /mgr/fields` | `GET /mgr/fields/{id}` |
|----------------|-------------------|------------------------|
| **Metadata** | ✅ Sí | ✅ Sí |
| **Data agregada** | ❌ No | ✅ Sí |
| **Múltiples KPIs** | ✅ Sí | ❌ No |
| **Paginado** | ✅ Sí | ❌ No |
| **Uso recomendado** | Listar KPIs | Análisis detallado |

---

## Referencias

- **Implementación:** `services/kpi_service.py` - Clase `KPIService`
- **Normalización:** `analytics/kpi_normalizer.py` - Clase `KPINormalizer`
- **Orquestación:** `orchestration/extract_kpis.py` - Clase `KPIExtractor`
- **Script:** `scripts/06_kpis.py`
