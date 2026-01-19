# Endpoint: GET /companies

## Descripción

Lista todas las empresas (companies) asociadas a una organización específica. 

**⚠️ IMPORTANTE:** En el dominio de Charly.io, "Company" representa un **ACTOR POSTULANTE**, no necesariamente una empresa jurídica formal. Puede ser una persona natural, emprendimiento individual, consultor o empresa formal.

---

## Especificación Técnica

| Propiedad | Valor |
|-----------|-------|
| **Método HTTP** | `GET` |
| **Path** | `/companies` |
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
GET https://app.charly.io/api/v1/companies?api_key=abc123...&organization_id=123
```

---

## Response

### Status Code: 200 OK

**Formato Paginado:**

```json
{
    "count": 150,
    "previous": null,
    "next": "https://app.charly.io/api/v1/companies?page=2&organization_id=123",
    "results": [
        {
            "id": 456,
            "name": "Mi Empresa SpA",
            "fantasy_name": "Mi Empresa",
            "email": "contacto@miempresa.com",
            "employee_size": "s",
            "first_name": null,
            "last_name": null,
            "organization_id": 123,
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-20T14:30:00Z"
        },
        {
            "id": 789,
            "name": "Juan Pérez",
            "fantasy_name": null,
            "email": "juan.perez@gmail.com",
            "employee_size": "xs",
            "first_name": "Juan",
            "last_name": "Pérez",
            "organization_id": 123,
            "created_at": "2024-02-01T09:00:00Z",
            "updated_at": "2024-02-10T16:45:00Z"
        }
    ]
}
```

### Campos de Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `count` | `integer` | Total de empresas en la organización |
| `previous` | `string\|null` | URL de la página anterior |
| `next` | `string\|null` | URL de la página siguiente |
| `results` | `array` | Lista de empresas en la página actual |

### Campos de Company

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `integer` | ID único de la empresa |
| `name` | `string` | Nombre o razón social |
| `fantasy_name` | `string\|null` | Nombre de fantasía (si aplica) |
| `email` | `string` | Email de contacto |
| `employee_size` | `string` | Tamaño: `xs`, `s`, `m`, `l`, `xl` |
| `first_name` | `string\|null` | Nombre (si es persona natural) |
| `last_name` | `string\|null` | Apellido (si es persona natural) |
| `organization_id` | `integer` | ID de la organización |
| `created_at` | `string` | Fecha de creación (ISO8601) |
| `updated_at` | `string` | Fecha de última actualización (ISO8601) |

---

## Ejemplo de Uso

### Usando CompanyService (Recomendado)

```python
from pathlib import Path
from orchestration.bootstrap import Bootstrap
from services.company_service import CompanyService

# Bootstrap
ctx = Bootstrap(config_path=Path("config/charly.yaml")).run()
client = ctx["client"]

# Listar empresas de una organización
company_service = CompanyService(client)
response = company_service.list_companies(organization_id=123)

print(f"Total empresas: {response['count']}")
for company in response['results']:
    print(f"- {company['name']} (ID: {company['id']})")
```

### Iteración Completa (Todas las Páginas)

```python
company_service = CompanyService(client)

# Iterar todas las empresas automáticamente
for company in company_service.iterate_companies(organization_id=123):
    print(f"- {company['name']} (ID: {company['id']})")
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
url = f"{base_url}/companies?{params}"

request = urllib.request.Request(url=url, method="GET")

with urllib.request.urlopen(request, timeout=30) as response:
    import json
    data = json.loads(response.read().decode("utf-8"))
    
    print(f"Total: {data['count']}")
    for company in data['results']:
        print(f"- {company['name']}")
```

---

## Interpretación de "Company"

### Empresa Formal

```json
{
    "id": 456,
    "name": "Mi Empresa SpA",
    "fantasy_name": "Mi Empresa",
    "first_name": null,
    "last_name": null,
    "employee_size": "s"
}
```

### Persona Natural

```json
{
    "id": 789,
    "name": "Juan Pérez",
    "fantasy_name": null,
    "first_name": "Juan",
    "last_name": "Pérez",
    "employee_size": "xs"
}
```

### Emprendimiento Individual

```json
{
    "id": 101,
    "name": "Consultoría XYZ",
    "fantasy_name": null,
    "first_name": "María",
    "last_name": "González",
    "employee_size": "xs"
}
```

---

## Paginación

Este endpoint es paginado. El sistema maneja automáticamente la paginación:

```python
# Paginación automática
for company in company_service.iterate_companies(organization_id=123):
    process_company(company)
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

### Caso 1: Listar Todas las Empresas de una Organización

```python
company_service = CompanyService(client)

companies = []
for company in company_service.iterate_companies(organization_id=123):
    companies.append(company)

print(f"Total empresas: {len(companies)}")
```

### Caso 2: Filtrar Empresas Formales vs Personas Naturales

```python
company_service = CompanyService(client)

empresas_formales = []
personas_naturales = []

for company in company_service.iterate_companies(organization_id=123):
    if company.get('first_name') and company.get('last_name'):
        personas_naturales.append(company)
    else:
        empresas_formales.append(company)

print(f"Empresas formales: {len(empresas_formales)}")
print(f"Personas naturales: {len(personas_naturales)}")
```

### Caso 3: Buscar Empresa por Email

```python
company_service = CompanyService(client)

target_email = "contacto@miempresa.com"
for company in company_service.iterate_companies(organization_id=123):
    if company['email'] == target_email:
        print(f"Encontrada: {company['name']} (ID: {company['id']})")
        break
```

---

## Script de Ejemplo

Ver `scripts/03_01_companies.py`:

```python
from orchestration.bootstrap import Bootstrap
from services.organization_service import OrganizationService
from services.company_service import CompanyService

ctx = Bootstrap(config_path=Path("config/charly.yaml")).run()
client = ctx["client"]

org_service = OrganizationService(client)
company_service = CompanyService(client)

# Seleccionar organización
organizations = org_service.list()
print("\n=== ORGANIZATIONS DISPONIBLES ===")
for org in organizations:
    print(f"- ID: {org['id']} | Nombre: {org['name']}")

org_id = int(input("\nIngrese el ID de la organización: "))

# Listar empresas
payload = company_service.list_companies(org_id)
print(f"\n=== COMPANIES (ORG {org_id}) ===")
print(f"Total: {payload.get('count')}")
pprint(payload.get("results", []))
```

---

## Notas Importantes

1. **Semántica de "Company":**
   - ⚠️ No asumir que "company" == empresa CORFO formal
   - Puede ser persona natural, emprendimiento o empresa formal
   - Verificar `first_name`/`last_name` para distinguir

2. **organization_id Requerido:**
   - Este parámetro es SIEMPRE requerido
   - No hay endpoint para listar todas las empresas sin organización

3. **Rendimiento:**
   - Organizaciones grandes pueden tener miles de empresas
   - Siempre usar `iterate_companies()` para paginación automática

---

## Referencias

- **Implementación:** `services/company_service.py` - Clase `CompanyService`
- **Script:** `scripts/03_01_companies.py`
- **Nota Importante:** Ver comentarios en `scripts/03_01_companies.py` sobre interpretación de "Company"
