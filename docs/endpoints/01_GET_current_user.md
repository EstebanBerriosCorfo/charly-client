# Endpoint: GET /current_user

## Descripción

Obtiene la información del usuario autenticado actualmente en la sesión. Este endpoint es útil para validar la autenticación y obtener el contexto del usuario (empresas asociadas, permisos, etc.).

---

## Especificación Técnica

| Propiedad | Valor |
|-----------|-------|
| **Método HTTP** | `GET` |
| **Path** | `/current_user` |
| **Requiere API Key** | ✅ Sí |
| **Paginado** | ❌ No |
| **Base URL** | `https://app.charly.io/api/v1` |

---

## Request

### Query Parameters

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `api_key` | `string` | ✅ Sí | API key obtenida de `/sessions` |

### URL Completa

```
GET https://app.charly.io/api/v1/current_user?api_key=abc123...
```

---

## Response

### Status Code: 200 OK

```json
{
    "id": 123,
    "email": "usuario@ejemplo.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "companies": [
        {
            "id": 456,
            "name": "Mi Empresa",
            "email": "contacto@miempresa.com"
        }
    ],
    "organizations": [
        {
            "id": 789,
            "name": "Organización ABC"
        }
    ],
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-20T14:30:00Z"
}
```

### Campos de Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `integer` | ID único del usuario |
| `email` | `string` | Email del usuario |
| `first_name` | `string` | Nombre del usuario |
| `last_name` | `string` | Apellido del usuario |
| `companies` | `array` | Lista de empresas asociadas al usuario |
| `organizations` | `array` | Lista de organizaciones asociadas |
| `created_at` | `string` | Fecha de creación (ISO8601) |
| `updated_at` | `string` | Fecha de última actualización (ISO8601) |

---

## Ejemplo de Uso

### Usando UserService (Recomendado)

```python
from pathlib import Path
from orchestration.bootstrap import Bootstrap
from services.user_service import UserService

# Bootstrap
ctx = Bootstrap(config_path=Path("config/charly.yaml")).run()
client = ctx["client"]

# Obtener usuario actual
user_service = UserService(client)
current_user = user_service.get_current_user()

print(f"Usuario: {current_user['email']}")
print(f"Empresas: {len(current_user.get('companies', []))}")
```

### Usando Bootstrap (Ya incluye current_user)

```python
from pathlib import Path
from orchestration.bootstrap import Bootstrap

ctx = Bootstrap(config_path=Path("config/charly.yaml")).run()

current_user = ctx["current_user"]
print(f"Usuario autenticado: {current_user['email']}")
```

### Request HTTP Directo

```python
import urllib.request
import urllib.parse

api_key = "tu_api_key_aqui"
base_url = "https://app.charly.io/api/v1"

params = urllib.parse.urlencode({"api_key": api_key})
url = f"{base_url}/current_user?{params}"

request = urllib.request.Request(url=url, method="GET")

with urllib.request.urlopen(request, timeout=30) as response:
    import json
    current_user = json.loads(response.read().decode("utf-8"))
    print(current_user)
```

---

## Validación de Entorno

Este endpoint se usa típicamente durante el bootstrap para validar que el usuario tiene acceso a empresas:

```python
def _validate_environment(self, current_user: Dict[str, Any]) -> None:
    """
    Validaciones mínimas de entorno antes de ejecutar casos de uso.
    """
    companies = current_user.get("companies", [])

    if not companies:
        raise CharlyApiError(
            message="Usuario no tiene empresas asociadas. Entorno inválido.",
            endpoint="/current_user",
        )
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

**Ejemplo de manejo:**

```python
from core.exceptions import AuthError

try:
    current_user = user_service.get_current_user()
except AuthError as e:
    print(f"Error de autenticación: {e.message}")
    # Renovar autenticación
```

### 403 Forbidden

Usuario no tiene permisos para acceder a este endpoint.

---

## Casos de Uso

### Caso 1: Validar Autenticación

```python
from services.user_service import UserService

user_service = UserService(client)

try:
    current_user = user_service.get_current_user()
    print(f"✅ Autenticación válida: {current_user['email']}")
except AuthError:
    print("❌ Autenticación inválida")
```

### Caso 2: Obtener Empresas del Usuario

```python
current_user = user_service.get_current_user()
companies = current_user.get("companies", [])

for company in companies:
    print(f"- {company['name']} (ID: {company['id']})")
```

### Caso 3: Validar Acceso a Organización

```python
current_user = user_service.get_current_user()
organizations = current_user.get("organizations", [])

org_ids = [org["id"] for org in organizations]

if target_org_id in org_ids:
    print("✅ Usuario tiene acceso a la organización")
else:
    print("❌ Usuario no tiene acceso")
```

---

## Script de Ejemplo

Ver `scripts/01_current_user.py`:

```python
from orchestration.bootstrap import Bootstrap
from services.user_service import UserService

ctx = Bootstrap(config_path=Path("config/charly.yaml")).run()
client = ctx["client"]

user_service = UserService(client)
current_user = user_service.get_current_user()

print("\n=== CURRENT USER ===")
pprint(current_user)
```

---

## Notas Importantes

1. **Validación en Bootstrap:**
   - Este endpoint se ejecuta automáticamente durante el bootstrap
   - Se valida que el usuario tenga empresas asociadas

2. **Contexto del Usuario:**
   - La información del usuario puede cambiar según la organización activa
   - Los `companies` y `organizations` reflejan el acceso actual

3. **Caché:**
   - El resultado se puede cachear durante la sesión
   - No es necesario llamarlo múltiples veces en el mismo flujo

---

## Referencias

- **Implementación:** `services/user_service.py` - Clase `UserService`
- **Bootstrap:** `orchestration/bootstrap.py` - Método `_load_current_user()`
- **Script:** `scripts/01_current_user.py`
