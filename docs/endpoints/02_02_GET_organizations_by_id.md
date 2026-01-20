# Endpoint: GET /organizations/{organization_id}

## Descripción

Obtiene el detalle completo de una organización específica por su ID. Incluye información adicional que no está disponible en el listado general.

---

## Especificación Técnica

| Propiedad | Valor |
|-----------|-------|
| **Método HTTP** | `GET` |
| **Path** | `/organizations/{organization_id}` |
| **Requiere API Key** | ✅ Sí |
| **Paginado** | ❌ No |
| **Base URL** | `https://app.charly.io/api/v1` |

---

## Request

### Path Parameters

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `organization_id` | `integer` | ✅ Sí | ID de la organización |

### Query Parameters

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `api_key` | `string` | ✅ Sí | API key obtenida de `/sessions` |

### URL Completa

```
GET https://app.charly.io/api/v1/organizations/123?api_key=abc123...
```

---

## Response

### Status Code: 200 OK

```json
{
    "id": 123,
    "name": "Organización ABC",
    "slug": "organizacion-abc",
    "description": "Descripción detallada de la organización",
    "website": "https://www.organizacion-abc.com",
    "logo_url": "https://cdn.charly.io/logos/org-123.png",
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-20T14:30:00Z",
    "settings": {
        "allow_public_applications": true,
        "require_company_verification": false
    },
    "metadata": {
        "region": "Región Metropolitana",
        "country": "Chile"
    }
}
```

### Campos de Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `integer` | ID único de la organización |
| `name` | `string` | Nombre de la organización |
| `slug` | `string` | Identificador URL-friendly |
| `description` | `string\|null` | Descripción detallada |
| `website` | `string\|null` | URL del sitio web |
| `logo_url` | `string\|null` | URL del logo |
| `created_at` | `string` | Fecha de creación (ISO8601) |
| `updated_at` | `string` | Fecha de última actualización (ISO8601) |
| `settings` | `object\|null` | Configuraciones de la organización |
| `metadata` | `object\|null` | Metadatos adicionales |

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

# Obtener organización por ID
org_service = OrganizationService(client)
organization = org_service.get_organization(organization_id=123)

print(f"Organización: {organization['name']}")
print(f"Descripción: {organization.get('description', 'N/A')}")
```

### Usando Alias

```python
# El método get_by_id() es un alias de get_organization()
organization = org_service.get_by_id(organization_id=123)
```

### Request HTTP Directo

```python
import urllib.request
import urllib.parse

api_key = "tu_api_key_aqui"
base_url = "https://app.charly.io/api/v1"
organization_id = 123

params = urllib.parse.urlencode({"api_key": api_key})
url = f"{base_url}/organizations/{organization_id}?{params}"

request = urllib.request.Request(url=url, method="GET")

with urllib.request.urlopen(request, timeout=30) as response:
    import json
    organization = json.loads(response.read().decode("utf-8"))
    print(organization)
```

---

## Manejo de Errores

### 404 Not Found

Organización no encontrada o usuario no tiene acceso.

```json
{
    "error": "Organization not found"
}
```

**Ejemplo de manejo:**

```python
from core.exceptions import CharlyApiError

try:
    organization = org_service.get_organization(organization_id=999)
except CharlyApiError as e:
    if e.status_code == 404:
        print("Organización no encontrada")
    else:
        print(f"Error: {e.message}")
```

### 401 Unauthorized

API key inválida o expirada.

### 403 Forbidden

Usuario no tiene permisos para acceder a esta organización.

---

## Casos de Uso

### Caso 1: Validar Acceso a Organización

```python
org_service = OrganizationService(client)

try:
    organization = org_service.get_organization(organization_id=123)
    print(f"✅ Acceso válido a: {organization['name']}")
except CharlyApiError as e:
    if e.status_code == 404:
        print("❌ Organización no encontrada o sin acceso")
```

### Caso 2: Obtener Metadatos de Organización

```python
organization = org_service.get_organization(organization_id=123)

metadata = organization.get("metadata", {})
print(f"Región: {metadata.get('region', 'N/A')}")
print(f"País: {metadata.get('country', 'N/A')}")
```

### Caso 3: Verificar Configuraciones

```python
organization = org_service.get_organization(organization_id=123)

settings = organization.get("settings", {})
if settings.get("allow_public_applications"):
    print("✅ Acepta postulaciones públicas")
```

---

## Script de Ejemplo

Ver `scripts/02_02_organization_by_id.py`:

```python
from orchestration.bootstrap import Bootstrap
from services.organization_service import OrganizationService

ctx = Bootstrap(config_path=Path("config/charly.yaml")).run()
client = ctx["client"]

org_service = OrganizationService(client)

# Listar organizaciones disponibles
organizations = org_service.list()
print("\n=== ORGANIZACIONES DISPONIBLES ===")
for org in organizations:
    print(f"- ID: {org['id']} | Nombre: {org['name']}")

# Obtener detalle de una organización
org_id = int(input("\nIngrese el ID de la organización: "))
organization = org_service.get_organization(org_id)

print("\n=== ORGANIZACIÓN (DETALLE) ===")
pprint(organization)
```

---

## Comparación con Listado

| Característica | `GET /organizations` | `GET /organizations/{id}` |
|----------------|---------------------|---------------------------|
| **Información básica** | ✅ Sí | ✅ Sí |
| **Descripción** | ❌ No | ✅ Sí |
| **Website/Logo** | ❌ No | ✅ Sí |
| **Settings** | ❌ No | ✅ Sí |
| **Metadata** | ❌ No | ✅ Sí |
| **Paginado** | ✅ Sí | ❌ No |

---

## Notas Importantes

1. **Validación de Acceso:**
   - El endpoint retorna 404 si el usuario no tiene acceso a la organización
   - Siempre validar el acceso antes de usar el ID en otros endpoints

2. **Rendimiento:**
   - Este endpoint es más costoso que el listado
   - Usar solo cuando necesites información detallada

3. **Cacheo:**
   - La información de organización cambia poco frecuentemente
   - Considerar cachear el resultado si se usa múltiples veces

---

## Referencias

- **Implementación:** `services/organization_service.py` - Clase `OrganizationService`
- **Script:** `scripts/02_02_organization_by_id.py`
