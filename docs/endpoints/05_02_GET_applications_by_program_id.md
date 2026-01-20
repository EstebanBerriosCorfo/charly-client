# Endpoint: GET /applications/{application_id}

## Descripción

Obtiene el detalle completo de una postulación específica, incluyendo **todas las respuestas (form_answers y field_answers)** y evaluaciones. Este es el endpoint más completo para obtener información detallada de una postulación.

**Script de uso masivo:** `05_02_GET_applications_by_program_id.py` - Permite obtener **todas las postulaciones de un programa completo** con las siguientes características:

- **Procesamiento paralelo optimizado**: 25 workers simultáneos para máxima velocidad (~10-12 aplicaciones/segundo)
- **Barra de progreso visual**: Muestra porcentaje, contador de filas procesadas, estadísticas (exitosas/fallidas), tasa de procesamiento y ETA
- **Exportación a Excel**: Genera archivo Excel con todas las columnas disponibles, incluyendo campos vacíos
- **Manejo automático de columnas duplicadas**: Renombra automáticamente columnas con el mismo nombre agregando números secuenciales (_2, _3, etc.)
- **Guardado de progreso**: Permite reanudar el procesamiento si se interrumpe
- **Validación de datos**: Detecta y reporta discrepancias entre datos procesados y exportados

---

## Especificación Técnica

| Propiedad | Valor |
|-----------|-------|
| **Método HTTP** | `GET` |
| **Path** | `/applications/{application_id}` |
| **Requiere API Key** | ✅ Sí |
| **Paginado** | ❌ No |
| **Base URL** | `https://app.charly.io/api/v1` |

---

## Request

### Path Parameters

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `application_id` | `integer` | ✅ Sí | ID de la postulación |

### Query Parameters

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `api_key` | `string` | ✅ Sí | API key obtenida de `/sessions` |

### URL Completa

```
GET https://app.charly.io/api/v1/applications/5678?api_key=abc123...
```

---

## Response

### Status Code: 200 OK

```json
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
        "email": "contacto@xyz.com",
        "phone": "+56 9 1234 5678"
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
                    "answer": "Mi Empresa SpA",
                    "field": {
                        "id": 4444,
                        "name": "field_empresa_nombre",
                        "question": "Nombre de la empresa",
                        "field_type": "text",
                        "component_type": "input"
                    }
                },
                {
                    "id": 3334,
                    "answer": "Desarrollo de software",
                    "field": {
                        "id": 4445,
                        "name": "field_actividad",
                        "question": "Actividad principal",
                        "field_type": "text",
                        "component_type": "textarea"
                    }
                }
            ]
        },
        {
            "id": 1112,
            "form_id": 2223,
            "answered_at": "2024-02-15T15:00:00Z",
            "form": {
                "id": 2223,
                "name": "Formulario Técnico",
                "title": "Información Técnica del Proyecto"
            },
            "field_answers": [
                {
                    "id": 3335,
                    "answer": "Python, Django, PostgreSQL",
                    "field": {
                        "id": 4446,
                        "name": "field_tecnologias",
                        "question": "Tecnologías utilizadas",
                        "field_type": "text",
                        "component_type": "textarea"
                    }
                }
            ]
        }
    ],
    "evaluations": [
        {
            "id": 5555,
            "evaluator_id": 6666,
            "evaluator_name": "Juan Evaluador",
            "score": 88.0,
            "comments": "Excelente propuesta técnica",
            "created_at": "2024-02-20T10:00:00Z"
        }
    ],
    "created_at": "2024-02-10T10:00:00Z",
    "updated_at": "2024-02-20T14:30:00Z"
}
```

### Campos de Respuesta

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
| `company` | `object` | Información completa de la empresa |
| `form_answers` | `array` | **Lista completa de respuestas de formularios** |
| `evaluations` | `array\|null` | Evaluaciones realizadas por evaluadores |
| `created_at` | `string` | Fecha de creación |
| `updated_at` | `string` | Fecha de actualización |

### Estructura de form_answers

Cada `form_answer` contiene:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `integer` | ID de la respuesta del formulario |
| `form_id` | `integer` | ID del formulario |
| `answered_at` | `string` | Fecha de respuesta |
| `form` | `object` | Información del formulario |
| `field_answers` | `array` | **Lista de respuestas a campos específicos** |

### Estructura de field_answers

Cada `field_answer` contiene:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `integer` | ID de la respuesta del campo |
| `answer` | `string\|number\|boolean\|array` | Valor de la respuesta |
| `field` | `object` | Información del campo (pregunta) |

### Estructura de field

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `integer` | ID del campo |
| `name` | `string` | Nombre técnico del campo |
| `question` | `string` | Pregunta visible al usuario |
| `field_type` | `string` | Tipo: `text`, `number`, `boolean`, `date`, etc. |
| `component_type` | `string` | Componente UI: `input`, `textarea`, `select`, etc. |

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

# Obtener postulación completa
application_service = ApplicationService(client)
application = application_service.get_application(application_id=5678)

print(f"Postulación: {application['name']}")
print(f"Programa ID: {application['program_id']}")
print(f"Empresa: {application['company']['name']}")
print(f"Puntaje evaluación: {application.get('score_eval', 'N/A')}")

# Iterar respuestas
for form_answer in application.get('form_answers', []):
    print(f"\nFormulario: {form_answer['form']['name']}")
    for field_answer in form_answer.get('field_answers', []):
        field = field_answer['field']
        print(f"  - {field['question']}: {field_answer['answer']}")
```

### Normalización para BI

```python
from analytics.application_normalizer import ApplicationNormalizer

application_service = ApplicationService(client)
normalizer = ApplicationNormalizer()

# Obtener postulación
application = application_service.get_application(application_id=5678)

# Normalizar en tablas planas
normalized = normalizer.normalize_application_full(application)

# Tablas listas para BI/Excel
applications_table = normalized["applications"]
form_answers_table = normalized["form_answers"]
field_answers_table = normalized["field_answers"]

print(f"Metadata: {len(applications_table)} fila(s)")
print(f"Respuestas formularios: {len(form_answers_table)} fila(s)")
print(f"Respuestas campos: {len(field_answers_table)} fila(s)")
```

### Extracción de Respuestas Específicas

```python
application = application_service.get_application(application_id=5678)

# Buscar respuesta específica por nombre de campo
target_field_name = "field_empresa_nombre"
for form_answer in application.get('form_answers', []):
    for field_answer in form_answer.get('field_answers', []):
        if field_answer['field']['name'] == target_field_name:
            print(f"Respuesta encontrada: {field_answer['answer']}")
            break
```

### Request HTTP Directo

```python
import urllib.request
import urllib.parse

api_key = "tu_api_key_aqui"
base_url = "https://app.charly.io/api/v1"
application_id = 5678

params = urllib.parse.urlencode({"api_key": api_key})
url = f"{base_url}/applications/{application_id}?{params}"

request = urllib.request.Request(url=url, method="GET")

with urllib.request.urlopen(request, timeout=30) as response:
    import json
    application = json.loads(response.read().decode("utf-8"))
    
    print(f"Postulación: {application['name']}")
    print(f"Total formularios: {len(application.get('form_answers', []))}")
```

---

## Manejo de Errores

### 404 Not Found

Postulación no encontrada o usuario no tiene acceso.

```json
{
    "error": "Application not found"
}
```

**Ejemplo de manejo:**

```python
from core.exceptions import CharlyApiError

try:
    application = application_service.get_application(application_id=9999)
except CharlyApiError as e:
    if e.status_code == 404:
        print("Postulación no encontrada")
    else:
        print(f"Error: {e.message}")
```

### 401 Unauthorized

API key inválida o expirada.

### 403 Forbidden

Usuario no tiene permisos para acceder a esta postulación.

---

## Casos de Uso

### Caso 1: Análisis Completo de una Postulación

```python
application_service = ApplicationService(client)
application = application_service.get_application(application_id=5678)

# Información básica
print(f"Postulación: {application['name']}")
print(f"Estado: {application['application_status']}")
print(f"Empresa: {application['company']['name']}")

# Puntajes
scores = {
    'admin': application.get('score_admin'),
    'algo': application.get('score_algo'),
    'eval': application.get('score_eval')
}
print(f"Puntajes: {scores}")

# Respuestas
for form_answer in application.get('form_answers', []):
    print(f"\nFormulario: {form_answer['form']['name']}")
    for field_answer in form_answer.get('field_answers', []):
        print(f"  {field_answer['field']['question']}: {field_answer['answer']}")
```

### Caso 2: Extracción de Datos para Excel

```python
from analytics.application_normalizer import ApplicationNormalizer
import pandas as pd

application_service = ApplicationService(client)
normalizer = ApplicationNormalizer()

application = application_service.get_application(application_id=5678)
normalized = normalizer.normalize_application_full(application)

# Crear DataFrames
df_applications = pd.DataFrame(normalized["applications"])
df_form_answers = pd.DataFrame(normalized["form_answers"])
df_field_answers = pd.DataFrame(normalized["field_answers"])

# Exportar a Excel
with pd.ExcelWriter("postulacion_5678.xlsx") as writer:
    df_applications.to_excel(writer, sheet_name="Applications", index=False)
    df_form_answers.to_excel(writer, sheet_name="Form Answers", index=False)
    df_field_answers.to_excel(writer, sheet_name="Field Answers", index=False)
```

### Caso 3: Validación de Completitud

```python
application = application_service.get_application(application_id=5678)

# Verificar que todos los formularios tienen respuestas
form_answers_count = len(application.get('form_answers', []))
expected_count = application.get('form_answers_count', 0)

if form_answers_count == expected_count:
    print("✅ Todos los formularios tienen respuestas")
else:
    print(f"⚠️ Faltan respuestas: {expected_count - form_answers_count}")

# Verificar evaluaciones
evaluations = application.get('evaluations', [])
if len(evaluations) > 0:
    print(f"✅ Tiene {len(evaluations)} evaluación(es)")
else:
    print("⚠️ No tiene evaluaciones aún")
```

---

## Normalización de Datos

Este endpoint es ideal para normalización usando `ApplicationNormalizer`:

### Tablas Generadas

1. **applications_table** (1 fila por postulación)
   - Metadata básica: ID, nombre, estado, puntajes, empresa

2. **form_answers_table** (N filas, una por formulario respondido)
   - Relación: application_id → form_answer_id → form_id

3. **field_answers_table** (N filas, una por respuesta a campo)
   - Relación: application_id → form_answer_id → field_answer_id → field_id
   - Incluye pregunta, respuesta, tipo de campo

### Ejemplo de Normalización

```python
from analytics.application_normalizer import ApplicationNormalizer

normalizer = ApplicationNormalizer()
application = application_service.get_application(application_id=5678)

normalized = normalizer.normalize_application_full(application)

# Estructura normalizada lista para BI
print(normalized.keys())
# dict_keys(['applications', 'form_answers', 'field_answers'])
```

---

## Notas Importantes

1. **Endpoint Completo:**
   - ✅ Incluye TODAS las respuestas (form_answers y field_answers)
   - ✅ Incluye evaluaciones si están disponibles
   - ✅ Información completa de la empresa

2. **Rendimiento:**
   - Este endpoint puede ser pesado si la postulación tiene muchos formularios
   - Ideal para análisis detallado de postulaciones individuales

3. **Uso Recomendado:**
   - Para análisis individual: usar este endpoint
   - Para análisis masivo: usar `GET /applications` con `include_data=true` o normalizar múltiples postulaciones

4. **Normalización:**
   - Siempre usar `ApplicationNormalizer` para convertir a tablas planas
   - Facilita análisis en Excel, Power BI, SQL, etc.

---

## Comparación con Otros Endpoints

| Característica | `GET /applications/{id}` | `GET /applications` (include_data=true) |
|----------------|-------------------------|----------------------------------------|
| **Una postulación** | ✅ Sí | ❌ No (múltiples) |
| **Respuestas completas** | ✅ Sí | ✅ Sí |
| **Evaluaciones** | ✅ Sí | ✅ Sí |
| **Rendimiento** | ✅ Óptimo para una | ⚠️ Costoso para muchas |
| **Uso recomendado** | Análisis individual | Extracción masiva |

---

## Referencias

- **Implementación:** `services/application_service.py` - Clase `ApplicationService`
- **Normalización:** `utils/dataframe_builder.py` - Función `build_applications_dataframe`
- **Exportación:** `utils/excel_exporter.py` - Función `export_applications_dataframe_to_excel`
- **Script Principal:** 
  - `scripts/05_02_GET_applications_by_program_id.py` - Obtener todas las postulaciones de un programa con respuestas completas
    - Procesamiento paralelo optimizado (25 workers simultáneos)
    - Barra de progreso visual con porcentaje y estadísticas
    - Exportación a Excel con todas las columnas (incluyendo campos vacíos)
    - Manejo automático de columnas duplicadas con renombrado secuencial
    - Guardado de progreso para reanudar procesamiento
    - Validación de datos y detección de discrepancias
