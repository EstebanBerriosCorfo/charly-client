# Análisis del Flujo Completo de Consumo de API Charly.io

## Resumen Ejecutivo

Este documento describe el flujo completo asociado al consumo de los diversos endpoints de la API de Charly.io para acceder a los datos de **convocatorias de postulación y evaluación** almacenados en la plataforma.

---

## 1. Arquitectura General del Sistema

El sistema está estructurado en capas claramente definidas:

```
┌─────────────────────────────────────────────────────────┐
│                    ORCHESTRATION                        │
│  (extract_programs.py, extract_kpis.py, bootstrap.py)   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                      SERVICES                            │
│  (ProgramService, ApplicationService, KPIService, etc.) │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                    CORE CLIENT                           │
│  (CharlyApiClient, Auth, Endpoints Registry)            │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                    API CHARLY.IO                        │
│              (https://app.charly.io/api/v1)              │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Flujo de Autenticación y Bootstrap

### 2.1. Inicialización del Sistema

El flujo comienza con el **Bootstrap** (`orchestration/bootstrap.py`):

```python
Bootstrap(config_path="config/charly.yaml").run()
```

**Pasos del Bootstrap:**

1. **Resolución del Usuario del Sistema**
   - `SystemUserResolver.resolve()` obtiene el usuario del sistema operativo
   - Identifica el usuario para almacenar credenciales de forma segura

2. **Carga de Credenciales**
   - `CredentialStore` carga las credenciales Charly del usuario desde `_charly_secrets/charly_users.json`
   - Formato: `{"username": "email@example.com", "password": "..."}`

3. **Autenticación contra Charly**
   - Endpoint: `POST /sessions`
   - Implementación: `CharlyAuth.create_session(username, password)`
   - **No requiere API key** (es el único endpoint que no la necesita)
   - Respuesta: `{"api_key": "..."}`

4. **Persistencia de API Key**
   - `ApiKeyStore` guarda la API key en `_charly_secrets/api_keys.json`
   - Formato: `{"system_user": "api_key"}`

5. **Construcción del Cliente API**
   - `CharlyApiClient` se inicializa con:
     - `api_key`: obtenida del paso anterior
     - `base_url`: desde configuración (`config/charly.yaml`)
     - `timeout`: 120 segundos por defecto
     - `RateLimitHandler`: manejo de rate limiting

6. **Validación del Entorno**
   - `GET /current_user` para obtener información del usuario activo
   - Validación: usuario debe tener empresas asociadas

**Resultado del Bootstrap:**
```python
{
    "system_user": "usuario_sistema",
    "api_key": "api_key_valida",
    "client": CharlyApiClient,
    "current_user": {...}
}
```

---

## 3. Endpoints Principales para Convocatorias y Evaluaciones

### 3.1. Registro Central de Endpoints

Todos los endpoints están registrados en `core/endpoints.py`:

| Endpoint | Método | Path | Paginado | Descripción |
|----------|--------|------|----------|-------------|
| `create_session` | POST | `/sessions` | No | Autenticación |
| `current_user` | GET | `/current_user` | No | Usuario activo |
| `list_organizations` | GET | `/organizations` | Sí | Listar organizaciones |
| `list_programs` | GET | `/programs` | Sí | Listar convocatorias |
| `get_program` | GET | `/programs/{program_id}` | No | Convocatoria con postulaciones |
| `list_applications` | GET | `/applications` | Sí | Listar postulaciones |
| `get_application` | GET | `/applications/{application_id}` | No | Postulación con respuestas |
| `list_kpis` | GET | `/mgr/fields` | Sí | Listar KPIs |
| `get_kpi` | GET | `/mgr/fields/{field_id}` | No | KPI con data agregada |

---

## 4. Flujo de Obtención de Convocatorias (Programs)

### 4.1. Listado de Convocatorias

**Servicio:** `ProgramService` (`services/program_service.py`)

**Endpoint:** `GET /programs`

**Filtros Disponibles:**
- `organization_id`: Filtrar por organización
- `application_status`: `draft` | `open` | `finished`
- `evaluation_status`: `draft` | `open` | `finished`
- `created_at`: Fecha mínima (YYYY-MM-DD)

**Ejemplo de Uso:**
```python
program_service = ProgramService(client)

# Listado simple (primera página)
response = program_service.list_programs(
    organization_id=123,
    application_status="open",
    evaluation_status="open"
)

# Iteración completa (todas las páginas)
for program in program_service.iterate_programs(
    organization_id=123,
    application_status="open"
):
    print(program["name"])
```

**Respuesta Paginada:**
```json
{
    "count": 150,
    "previous": null,
    "next": "https://app.charly.io/api/v1/programs?page=2",
    "results": [
        {
            "id": 1234,
            "name": "Convocatoria 2024",
            "organization_id": 123,
            "application_status": "open",
            "evaluation_status": "open",
            "created_at": "2024-01-15T10:00:00Z",
            ...
        }
    ]
}
```

### 4.2. Detalle de Convocatoria con Postulaciones

**Endpoint:** `GET /programs/{program_id}`

**Filtros Adicionales:**
- `company_application_status`: `pending` | `complete` | `sent`

**Ejemplo de Uso:**
```python
program_detail = program_service.get_program(
    program_id=1234,
    company_application_status="sent"
)
```

**Respuesta:**
```json
{
    "id": 1234,
    "name": "Convocatoria 2024",
    "organization_id": 123,
    "application_status": "open",
    "evaluation_status": "open",
    "applications": [
        {
            "id": 5678,
            "program_id": 1234,
            "name": "Postulación Empresa XYZ",
            "application_status": "sent",
            "company_application_status": "sent",
            "company": {
                "id": 999,
                "name": "Empresa XYZ",
                "email": "contacto@xyz.com"
            },
            "form_answers": [...],
            "score_admin": 85.5,
            "score_algo": 90.0,
            "score_eval": 88.0,
            ...
        }
    ]
}
```

---

## 5. Flujo de Obtención de Postulaciones (Applications)

### 5.1. Listado de Postulaciones

**Servicio:** `ApplicationService` (`services/application_service.py`)

**Endpoint:** `GET /applications`

**Filtros Disponibles:**
- `start_date`: Fecha mínima (ISO8601, YYYY-MM-DD)
- `end_date`: Fecha máxima (ISO8601, YYYY-MM-DD)
- `date_type`: `created_at` | `updated_at`
- `ids`: Lista de IDs separados por coma
- `include_data`: `true` para incluir respuestas y evaluaciones (costoso)

**Ejemplo de Uso:**
```python
application_service = ApplicationService(client)

# Listado con filtros temporales
for application in application_service.iterate_applications(
    start_date="2024-01-01",
    end_date="2024-12-31",
    date_type="created_at",
    include_data=False  # Solo metadata
):
    print(f"Postulación {application['id']}: {application['name']}")
```

### 5.2. Detalle de Postulación con Respuestas

**Endpoint:** `GET /applications/{application_id}`

**Ejemplo de Uso:**
```python
application_detail = application_service.get_application(
    application_id=5678
)
```

**Respuesta Completa:**
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
    ]
}
```

---

## 6. Flujo de Obtención de KPIs y Evaluaciones

### 6.1. Listado de KPIs

**Servicio:** `KPIService` (`services/kpi_service.py`)

**Endpoint:** `GET /mgr/fields`

**Parámetros:**
- `organization_id`: ID de la organización (requerido)

**Ejemplo de Uso:**
```python
kpi_service = KPIService(client)

for kpi in kpi_service.iterate_kpis(organization_id=123):
    print(f"KPI {kpi['id']}: {kpi['question']}")
```

### 6.2. Detalle de KPI con Data Agregada

**Endpoint:** `GET /mgr/fields/{field_id}`

**Ejemplo de Uso:**
```python
kpi_detail = kpi_service.get_kpi(
    field_id=4444,
    organization_id=123
)
```

**Respuesta:**
```json
{
    "id": 4444,
    "organization_id": 123,
    "field_type": "text",
    "component_type": "input",
    "field_function": "kpi",
    "weight": 10,
    "question": "Nombre de la empresa",
    "description": "Campo para capturar el nombre",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z",
    "data": {
        "labels": ["Ene", "Feb", "Mar"],
        "datasets": [
            {
                "label": "Postulaciones",
                "data": [10, 15, 20]
            }
        ]
    }
}
```

---

## 7. Orquestación Completa: Extracción de Programas y Postulaciones

### 7.1. ProgramExtractor

**Archivo:** `orchestration/extract_programs.py`

**Flujo Jerárquico:**
```
Organizations → Programs → Applications
```

**Ejemplo de Uso:**
```python
extractor = ProgramExtractor(client)

result = extractor.extract(
    organization_ids=[123],  # Opcional: None = todas
    program_filters={
        "application_status": "open",
        "evaluation_status": "open"
    },
    application_filters={}
)
```

**Estructura de Salida:**
```json
{
    "organizations": [
        {
            "organization": {
                "id": 123,
                "name": "Organización ABC"
            },
            "programs": [
                {
                    "program": {
                        "id": 1234,
                        "name": "Convocatoria 2024",
                        ...
                    },
                    "applications": [
                        {
                            "id": 5678,
                            "name": "Postulación XYZ",
                            ...
                        }
                    ]
                }
            ]
        }
    ]
}
```

---

## 8. Normalización de Datos para BI/Analytics

### 8.1. Normalización de Postulaciones

**Archivo:** `analytics/application_normalizer.py`

**Clase:** `ApplicationNormalizer`

**Tablas Generadas:**

1. **applications_table** (Nivel 1 - Metadata)
   - `application_id`, `program_id`, `application_name`
   - `application_status`, `company_application_status`
   - `score_admin`, `score_algo`, `score_eval`
   - `company_id`, `company_name`, `company_email`

2. **form_answers_table** (Nivel 2 - Respuestas por Formulario)
   - `application_id`, `form_answer_id`, `form_id`
   - `form_name`, `form_title`, `answered_at`

3. **field_answers_table** (Nivel 3 - Respuestas por Campo)
   - `application_id`, `program_id`, `company_id`
   - `form_answer_id`, `field_answer_id`, `field_id`
   - `field_name`, `field_question`, `field_type`
   - `component_type`, `answer`, `answered_at`

**Ejemplo de Uso:**
```python
from analytics.application_normalizer import ApplicationNormalizer

normalized = ApplicationNormalizer.normalize_application_full(application_detail)

# normalized = {
#     "applications": [...],
#     "form_answers": [...],
#     "field_answers": [...]
# }
```

### 8.2. Normalización de KPIs

**Archivo:** `analytics/kpi_normalizer.py`

**Clase:** `KPINormalizer`

**Tablas Generadas:**

1. **kpi_metadata_table**
   - `field_id`, `organization_id`, `field_type`
   - `component_type`, `field_function`, `weight`
   - `question`, `description`, `created_at`, `updated_at`

2. **kpi_data_table**
   - `field_id`, `organization_id`
   - `label`, `dataset_label`, `value`

**Ejemplo de Uso:**
```python
from analytics.kpi_normalizer import KPINormalizer

normalized = KPINormalizer.normalize_kpi_full(kpi_detail)

# normalized = {
#     "kpi_metadata": [...],
#     "kpi_data": [...]
# }
```

---

## 9. Manejo de Paginación

### 9.1. PaginationIterator

**Archivo:** `utils/pagination.py`

**Funcionamiento:**
- Iterador genérico que maneja automáticamente la paginación
- Lee `next` de la respuesta y hace requests automáticos
- Buffer interno para eficiencia

**Uso:**
```python
# Automático a través del cliente
for item in client.paginate("/programs", params={"organization_id": 123}):
    process(item)
```

**Formato de Respuesta Esperado:**
```json
{
    "count": 100,
    "previous": null,
    "next": "https://app.charly.io/api/v1/programs?page=2",
    "results": [...]
}
```

---

## 10. Manejo de Rate Limiting

### 10.1. RateLimitHandler

**Archivo:** `utils/rate_limit.py`

**Características:**
- Backoff exponencial antes de requests
- Respeta header `Retry-After` de la API
- Máximo de 3 reintentos por defecto
- Backoff base: 2 segundos, máximo: 30 segundos

**Hooks:**
- `before_request()`: Espera si hubo rate limit previo
- `after_response()`: Resetea contadores
- `on_rate_limit()`: Maneja errores 429

**Integración:**
El `CharlyApiClient` integra automáticamente el `RateLimitHandler`:
```python
# Pre-request
rate_limit_handler.before_request()

# Request
response = urllib.request.urlopen(...)

# Post-response
rate_limit_handler.after_response(response)
```

---

## 11. Inyección de API Key

### 11.1. Estrategia de Inyección

**Implementación:** `CharlyApiClient.request()`

**Reglas:**
- **GET requests**: API key va en query params (`?api_key=...`)
- **POST/PUT/DELETE requests**: API key va en JSON body
- **Excepción**: `/sessions` no requiere API key

**Código:**
```python
if endpoint != "/sessions":
    if method == "GET":
        params["api_key"] = self.api_key
    else:
        json_body["api_key"] = self.api_key
```

---

## 12. Manejo de Errores

### 12.1. Jerarquía de Excepciones

**Archivo:** `core/exceptions.py`

1. **CharlyApiError**: Error general de la API
2. **AuthError**: Errores 401/403 (autenticación/permisos)
3. **RateLimitError**: Error 429 (rate limit excedido)

**Manejo en Client:**
```python
except urllib.error.HTTPError as e:
    if status == 429:
        raise RateLimitError(...)
    elif status in (401, 403):
        raise AuthError(...)
    else:
        raise CharlyApiError(...)
```

---

## 13. Flujo Completo de Ejemplo

### 13.1. Caso de Uso: Extraer Todas las Postulaciones de una Convocatoria

```python
from pathlib import Path
from orchestration.bootstrap import Bootstrap
from services.program_service import ProgramService
from analytics.application_normalizer import ApplicationNormalizer

# 1. Bootstrap
ctx = Bootstrap(config_path=Path("config/charly.yaml")).run()
client = ctx["client"]

# 2. Obtener convocatoria con postulaciones
program_service = ProgramService(client)
program_detail = program_service.get_program(program_id=1234)

# 3. Normalizar cada postulación
normalizer = ApplicationNormalizer()
all_applications = []
all_form_answers = []
all_field_answers = []

for application in program_detail.get("applications", []):
    normalized = normalizer.normalize_application_full(application)
    all_applications.extend(normalized["applications"])
    all_form_answers.extend(normalized["form_answers"])
    all_field_answers.extend(normalized["field_answers"])

# 4. Resultado listo para BI/Excel
result = {
    "applications": all_applications,
    "form_answers": all_form_answers,
    "field_answers": all_field_answers
}
```

---

## 14. Datos de Evaluación

### 14.1. Información de Evaluación Disponible

Los datos de evaluación están presentes en varios niveles:

1. **A Nivel de Convocatoria (Program)**
   - `evaluation_status`: `draft` | `open` | `finished`
   - Filtro disponible en `list_programs()`

2. **A Nivel de Postulación (Application)**
   - `score_admin`: Puntaje administrativo
   - `score_algo`: Puntaje algorítmico
   - `score_eval`: Puntaje de evaluación
   - `assigned_evaluators_count`: Número de evaluadores asignados

3. **A Nivel de Respuestas (Field Answers)**
   - Cada `field_answer` puede contener evaluaciones específicas
   - Los KPIs (`/mgr/fields`) pueden contener métricas agregadas de evaluación

### 14.2. Acceso a Datos de Evaluación

**Desde Convocatorias:**
```python
programs = program_service.iterate_programs(
    evaluation_status="finished"  # Solo convocatorias con evaluación finalizada
)
```

**Desde Postulaciones:**
```python
application = application_service.get_application(application_id=5678)
scores = {
    "admin": application.get("score_admin"),
    "algo": application.get("score_algo"),
    "eval": application.get("score_eval")
}
```

**Desde KPIs:**
```python
kpi = kpi_service.get_kpi(field_id=4444, organization_id=123)
# kpi["data"] contiene métricas agregadas de evaluación
```

---

## 15. Consideraciones de Rendimiento

### 15.1. Endpoints Costosos

- `GET /programs/{program_id}`: Incluye todas las postulaciones
- `GET /applications` con `include_data=true`: Incluye todas las respuestas
- `GET /applications/{application_id}`: Incluye todas las respuestas y evaluaciones

### 15.2. Recomendaciones

1. **Usar paginación** para listados grandes
2. **Evitar `include_data=true`** en listados masivos
3. **Usar filtros** para reducir el volumen de datos
4. **Respetar rate limits** con el `RateLimitHandler`
5. **Cachear API keys** usando `ApiKeyStore`

---

## 16. Configuración

### 16.1. Archivo de Configuración

**Archivo:** `config/charly.yaml`

```yaml
charly:
  environment: prod
  base_url:
    prod: https://app.charly.io/api/v1
    beta: https://beta.charly.io/api/v1
  
  http:
    timeout_seconds: 30
  
  rate_limit:
    max_retries: 3
    base_backoff_seconds: 2
    max_backoff_seconds: 30
```

### 16.2. Credenciales

**Archivos:**
- `_charly_secrets/charly_users.json`: Credenciales de usuario
- `_charly_secrets/api_keys.json`: API keys cacheadas

---

## 17. Diagrama de Flujo Completo

```
┌─────────────────────────────────────────────────────────────┐
│                    INICIO DEL PROCESO                        │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    BOOTSTRAP                                │
│  1. Resolver usuario sistema                                │
│  2. Cargar credenciales                                     │
│  3. POST /sessions → obtener API key                        │
│  4. Guardar API key                                         │
│  5. Crear CharlyApiClient                                   │
│  6. GET /current_user → validar entorno                     │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              OBTENER CONVOCATORIAS                          │
│  GET /programs (con filtros)                                │
│  - organization_id                                          │
│  - application_status                                        │
│  - evaluation_status                                        │
│  - created_at                                               │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│         OBTENER POSTULACIONES DE CONVOCATORIA               │
│  GET /programs/{program_id}                                 │
│  - Incluye todas las applications                           │
│  - Filtro: company_application_status                       │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│        OBTENER DETALLE DE POSTULACIÓN                       │
│  GET /applications/{application_id}                          │
│  - Incluye form_answers                                     │
│  - Incluye field_answers                                    │
│  - Incluye scores (admin, algo, eval)                      │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              NORMALIZACIÓN DE DATOS                         │
│  ApplicationNormalizer                                       │
│  - applications_table                                       │
│  - form_answers_table                                       │
│  - field_answers_table                                      │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              OBTENER KPIs Y EVALUACIONES                    │
│  GET /mgr/fields (por organización)                        │
│  GET /mgr/fields/{field_id} (con data agregada)            │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              NORMALIZACIÓN DE KPIs                          │
│  KPINormalizer                                              │
│  - kpi_metadata_table                                       │
│  - kpi_data_table                                           │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              EXPORTACIÓN / BI                               │
│  - DataFrames (pandas)                                      │
│  - Excel (openpyxl)                                         │
│  - SQL / Power BI                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 18. Resumen de Endpoints por Caso de Uso

### 18.1. Convocatorias y Postulaciones

| Caso de Uso | Endpoint | Método | Servicio |
|-------------|----------|--------|----------|
| Listar convocatorias | `/programs` | GET | `ProgramService.list_programs()` |
| Convocatoria con postulaciones | `/programs/{id}` | GET | `ProgramService.get_program()` |
| Listar postulaciones | `/applications` | GET | `ApplicationService.list_applications()` |
| Postulación con respuestas | `/applications/{id}` | GET | `ApplicationService.get_application()` |

### 18.2. Evaluaciones y KPIs

| Caso de Uso | Endpoint | Método | Servicio |
|-------------|----------|--------|----------|
| Listar KPIs | `/mgr/fields` | GET | `KPIService.list_kpis()` |
| KPI con data agregada | `/mgr/fields/{id}` | GET | `KPIService.get_kpi()` |

---

## 19. Conclusión

El sistema proporciona un flujo completo y estructurado para acceder a los datos de convocatorias, postulaciones y evaluaciones almacenados en Charly.io:

1. **Autenticación segura** con persistencia de API keys
2. **Acceso jerárquico** a datos: Organizations → Programs → Applications
3. **Paginación automática** para grandes volúmenes
4. **Rate limiting** con backoff exponencial
5. **Normalización** de datos para BI/Analytics
6. **Separación de responsabilidades** en capas claras

El diseño permite tanto consultas simples como extracciones masivas de datos, con normalización automática para su uso en herramientas de Business Intelligence.
