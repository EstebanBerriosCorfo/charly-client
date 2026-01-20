# Endpoint: GET /companies/{company_id}

## Descripción

Obtiene el detalle completo de una empresa específica dentro de una organización. Incluye información adicional que no está disponible en el listado general.

---

## Especificación Técnica

| Propiedad | Valor |
|-----------|-------|
| **Método HTTP** | `GET` |
| **Path** | `/companies/{company_id}` |
| **Requiere API Key** | ✅ Sí |
| **Paginado** | ❌ No |
| **Base URL** | `https://app.charly.io/api/v1` |

---

## Request

### Path Parameters

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `company_id` | `integer` | ✅ Sí | ID de la empresa |

### Query Parameters

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `api_key` | `string` | ✅ Sí | API key obtenida de `/sessions` |
| `organization_id` | `integer` | ✅ Sí | ID de la organización |

### URL Completa

```
GET https://app.charly.io/api/v1/companies/456?api_key=abc123...&organization_id=123
```

---

## Response

### Status Code: 200 OK

```json
{
    "id": 456,
    "name": "Mi Empresa SpA",
    "fantasy_name": "Mi Empresa",
    "email": "contacto@miempresa.com",
    "phone": "+56 9 1234 5678",
    "website": "https://www.miempresa.com",
    "employee_size": "s",
    "first_name": null,
    "last_name": null,
    "organization_id": 123,
    "address": {
        "street": "Av. Principal 123",
        "city": "Santiago",
        "region": "Región Metropolitana",
        "country": "Chile"
    },
    "tax_id": "76.123.456-7",
    "legal_representative": "Juan Pérez",
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-20T14:30:00Z",
    "metadata": {
        "industry": "Tecnología",
        "founded_year": 2020
    }
}
```

### Campos de Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `integer` | ID único de la empresa |
| `name` | `string` | Nombre o razón social |
| `fantasy_name` | `string\|null` | Nombre de fantasía |
| `email` | `string` | Email de contacto |
| `phone` | `string\|null` | Teléfono de contacto |
| `website` | `string\|null` | Sitio web |
| `employee_size` | `string` | Tamaño: `xs`, `s`, `m`, `l`, `xl` |
| `first_name` | `string\|null` | Nombre (si es persona natural) |
| `last_name` | `string\|null` | Apellido (si es persona natural) |
| `organization_id` | `integer` | ID de la organización |
| `address` | `object\|null` | Dirección completa |
| `tax_id` | `string\|null` | RUT o identificador tributario |
| `legal_representative` | `string\|null` | Representante legal |
| `created_at` | `string` | Fecha de creación (ISO8601) |
| `updated_at` | `string` | Fecha de última actualización (ISO8601) |
| `metadata` | `object\|null` | Metadatos adicionales |

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

# Obtener empresa por ID
company_service = CompanyService(client)
company = company_service.get_company(
    company_id=456,
    organization_id=123
)

print(f"Empresa: {company['name']}")
print(f"Email: {company['email']}")
if company.get('address'):
    print(f"Dirección: {company['address']}")
```

### Request HTTP Directo

```python
import urllib.request
import urllib.parse

api_key = "tu_api_key_aqui"
base_url = "https://app.charly.io/api/v1"
company_id = 456
organization_id = 123

params = urllib.parse.urlencode({
    "api_key": api_key,
    "organization_id": organization_id
})
url = f"{base_url}/companies/{company_id}?{params}"

request = urllib.request.Request(url=url, method="GET")

with urllib.request.urlopen(request, timeout=30) as response:
    import json
    company = json.loads(response.read().decode("utf-8"))
    print(company)
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

Empresa no encontrada o no pertenece a la organización especificada.

```json
{
    "error": "Company not found"
}
```

**Ejemplo de manejo:**

```python
from core.exceptions import CharlyApiError

try:
    company = company_service.get_company(
        company_id=999,
        organization_id=123
    )
except CharlyApiError as e:
    if e.status_code == 404:
        print("Empresa no encontrada o no pertenece a la organización")
    else:
        print(f"Error: {e.message}")
```

### 401 Unauthorized

API key inválida o expirada.

### 403 Forbidden

Usuario no tiene permisos para acceder a esta empresa.

---

## Casos de Uso

### Caso 1: Validar Acceso a Empresa

```python
company_service = CompanyService(client)

try:
    company = company_service.get_company(
        company_id=456,
        organization_id=123
    )
    print(f"✅ Acceso válido a: {company['name']}")
except CharlyApiError as e:
    if e.status_code == 404:
        print("❌ Empresa no encontrada o sin acceso")
```

### Caso 2: Obtener Información Fiscal

```python
company = company_service.get_company(
    company_id=456,
    organization_id=123
)

if company.get('tax_id'):
    print(f"RUT: {company['tax_id']}")
if company.get('legal_representative'):
    print(f"Representante Legal: {company['legal_representative']}")
```

### Caso 3: Verificar Tipo de Empresa

```python
company = company_service.get_company(
    company_id=456,
    organization_id=123
)

if company.get('first_name') and company.get('last_name'):
    print(f"Persona Natural: {company['first_name']} {company['last_name']}")
else:
    print(f"Empresa Formal: {company['name']}")
    if company.get('tax_id'):
        print(f"RUT: {company['tax_id']}")
```

---

## Script de Ejemplo

Ver `scripts/03_02_company_by_id.py`:

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
print("\n=== ORGANIZACIONES DISPONIBLES ===")
for org in organizations:
    print(f"- ID: {org['id']} | Nombre: {org['name']}")

org_id = int(input("\nIngrese el ID de la organización: "))

# Listar empresas
companies = list(company_service.iterate_companies(org_id))
print("\n=== EMPRESAS DISPONIBLES ===")
for company in companies:
    print(f"- ID: {company['id']} | Nombre: {company['name']}")

company_id = int(input("\nIngrese el ID de la empresa: "))

# Obtener detalle
company = company_service.get_company(company_id, org_id)
print("\n=== EMPRESA (DETALLE) ===")
pprint(company)
```

---

## Comparación con Listado

| Característica | `GET /companies` | `GET /companies/{id}` |
|----------------|------------------|----------------------|
| **Información básica** | ✅ Sí | ✅ Sí |
| **Phone/Website** | ❌ No | ✅ Sí |
| **Address** | ❌ No | ✅ Sí |
| **Tax ID** | ❌ No | ✅ Sí |
| **Legal Representative** | ❌ No | ✅ Sí |
| **Metadata** | ❌ No | ✅ Sí |
| **Paginado** | ✅ Sí | ❌ No |

---

## Notas Importantes

1. **organization_id Requerido:**
   - Este parámetro es SIEMPRE requerido
   - La empresa debe pertenecer a la organización especificada

2. **Validación de Acceso:**
   - El endpoint retorna 404 si la empresa no pertenece a la organización
   - Siempre validar el acceso antes de usar el ID en otros endpoints

3. **Rendimiento:**
   - Este endpoint es más costoso que el listado
   - Usar solo cuando necesites información detallada

---

## Referencias

- **Implementación:** `services/company_service.py` - Clase `CompanyService`
- **Script:** `scripts/03_02_company_by_id.py`
