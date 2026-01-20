# Endpoint: GET /organizations

## Descripción

Lista todas las organizaciones disponibles para el usuario autenticado. Las organizaciones representan entidades que gestionan convocatorias y programas en Charly.io.

---

## Especificación Técnica

| Propiedad | Valor |
|-----------|-------|
| **Método HTTP** | `GET` |
| **Path** | `/organizations` |
| **Requiere API Key** | ✅ Sí |
| **Paginado** | ✅ Sí |
| **Base URL** | `https://app.charly.io/api/v1` |

---

## Request

### Query Parameters

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `api_key` | `string` | ✅ Sí | API key obtenida de `/sessions` |
| `page` | `integer` | ❌ No | Número de página (paginación) |

### URL Completa

```
GET https://app.charly.io/api/v1/organizations?api_key=abc123...
```

---

## Response

### Status Code: 200 OK

**Formato Paginado:**

```json
{
    "count": 5,
    "previous": null,
    "next": "https://app.charly.io/api/v1/organizations?page=2",
    "results": [
        {
            "id": 123,
            "name": "Organización ABC",
            "slug": "organizacion-abc",
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-20T14:30:00Z"
        },
        {
            "id": 456,
            "name": "Organización XYZ",
            "slug": "organizacion-xyz",
            "created_at": "2024-02-01T09:00:00Z",
            "updated_at": "2024-02-10T16:45:00Z"
        }
    ]
}
```

### Campos de Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `count` | `integer` | Total de organizaciones disponibles |
| `previous` | `string\|null` | URL de la página anterior (null si es primera) |
| `next` | `string\|null` | URL de la página siguiente (null si es última) |
| `results` | `array` | Lista de organizaciones en la página actual |

### Campos de Organización

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `integer` | ID único de la organización |
| `name` | `string` | Nombre de la organización |
| `slug` | `string` | Identificador URL-friendly |
| `created_at` | `string` | Fecha de creación (ISO8601) |
| `updated_at` | `string` | Fecha de última actualización (ISO8601) |

---

## Ejemplo de Uso

### Usando OrganizationService (Recomendado)

```python
from pathlib import Path
from orchestration.bootstrap import Bootstrap
from services.organization_service import OrganizationService

# Bootstrap
ctx = Bootstrap(config_path=Path("config/charly.yaml")).run()
client = ctx["client"]

# Listar organizaciones (primera página)
org_service = OrganizationService(client)
response = org_service.list_organizations()

print(f"Total organizaciones: {response['count']}")
for org in response['results']:
    print(f"- {org['name']} (ID: {org['id']})")
```

### Iteración Completa (Todas las Páginas)

```python
org_service = OrganizationService(client)

# Iterar todas las organizaciones automáticamente
for organization in org_service.iterate_organizations():
    print(f"- {organization['name']} (ID: {organization['id']})")
```

### Listado Simple (Solo Results)

```python
# Método conveniente que retorna solo la lista
organizations = org_service.list()

for org in organizations:
    print(f"- {org['name']} (ID: {org['id']})")
```

### Request HTTP Directo

```python
import urllib.request
import urllib.parse

api_key = "tu_api_key_aqui"
base_url = "https://app.charly.io/api/v1"

params = urllib.parse.urlencode({"api_key": api_key})
url = f"{base_url}/organizations?{params}"

request = urllib.request.Request(url=url, method="GET")

with urllib.request.urlopen(request, timeout=30) as response:
    import json
    data = json.loads(response.read().decode("utf-8"))
    
    print(f"Total: {data['count']}")
    for org in data['results']:
        print(f"- {org['name']}")
    
    # Manejar paginación manualmente
    if data.get('next'):
        # Hacer request a data['next']
        pass
```

---

## Paginación

Este endpoint es paginado. El sistema maneja automáticamente la paginación:

### Paginación Automática (Recomendado)

```python
# El método iterate_organizations() maneja la paginación automáticamente
for org in org_service.iterate_organizations():
    process_organization(org)
```

### Paginación Manual

```python
response = org_service.list_organizations()

while response:
    for org in response['results']:
        process_organization(org)
    
    # Obtener siguiente página
    if response.get('next'):
        # Extraer endpoint de la URL completa
        next_endpoint = response['next'].replace(base_url, '')
        response = client.request("GET", next_endpoint)
    else:
        response = None
```

---

## Manejo de Errores

### 401 Unauthorized

API key inválida o expirada.

```json
{
    "error": "Invalid API key"
}
```

### 403 Forbidden

Usuario no tiene permisos para listar organizaciones.

### 429 Too Many Requests

Rate limit excedido. El sistema maneja automáticamente con backoff.

---

## Casos de Uso

### Caso 1: Listar Todas las Organizaciones

```python
org_service = OrganizationService(client)

organizations = []
for org in org_service.iterate_organizations():
    organizations.append(org)

print(f"Total organizaciones: {len(organizations)}")
```

### Caso 2: Buscar Organización por Nombre

```python
org_service = OrganizationService(client)

target_name = "Organización ABC"
for org in org_service.iterate_organizations():
    if org['name'] == target_name:
        print(f"Encontrada: {org['name']} (ID: {org['id']})")
        break
```

### Caso 3: Obtener Primera Organización Disponible

```python
org_service = OrganizationService(client)

# Obtener primera organización
first_org = next(org_service.iterate_organizations(), None)
if first_org:
    print(f"Primera organización: {first_org['name']}")
```

---

## Script de Ejemplo

Ver `scripts/02_01_organizations.py`:

```python
from orchestration.bootstrap import Bootstrap
from services.organization_service import OrganizationService

ctx = Bootstrap(config_path=Path("config/charly.yaml")).run()
client = ctx["client"]

service = OrganizationService(client)
organizations = service.list()

print("\n=== ORGANIZATIONS (LIST) ===")
pprint(organizations)
```

---

## Notas Importantes

1. **Paginación:**
   - Siempre usar `iterate_organizations()` para obtener todas las organizaciones
   - El método maneja automáticamente múltiples páginas

2. **Filtros:**
   - Este endpoint no acepta filtros adicionales
   - Retorna todas las organizaciones accesibles por el usuario

3. **Rendimiento:**
   - Si solo necesitas la primera organización, usa `list()` y toma el primer elemento
   - Para múltiples organizaciones, usa `iterate_organizations()`

---

## Referencias

- **Implementación:** `services/organization_service.py` - Clase `OrganizationService`
- **Paginación:** `utils/pagination.py` - Clase `PaginationIterator`
- **Script:** `scripts/02_01_organizations.py`
