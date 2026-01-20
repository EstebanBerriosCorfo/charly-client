# Endpoint: POST /sessions

## Descripción

Endpoint de autenticación que permite crear una sesión en Charly.io y obtener una API key válida para realizar requests autenticados a la API.

**⚠️ IMPORTANTE:** Este es el único endpoint que NO requiere API key en el request.

---

## Especificación Técnica

| Propiedad | Valor |
|-----------|-------|
| **Método HTTP** | `POST` |
| **Path** | `/sessions` |
| **Requiere API Key** | ❌ No |
| **Paginado** | ❌ No |
| **Base URL** | `https://app.charly.io/api/v1` |

---

## Request

### Headers

```
Content-Type: application/json
```

### Body (JSON)

```json
{
    "username": "usuario@ejemplo.com",
    "password": "contraseña_segura"
}
```

### Parámetros del Body

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `username` | `string` | ✅ Sí | Email del usuario registrado en Charly.io |
| `password` | `string` | ✅ Sí | Contraseña del usuario |

---

## Response

### Status Code: 200 OK

```json
{
    "api_key": "abc123def456ghi789jkl012mno345pqr678stu901vwx234yz"
}
```

### Campos de Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `api_key` | `string` | API key válida para autenticar requests posteriores |

---

## Ejemplo de Uso

### Usando CharlyAuth (Recomendado)

```python
from core.auth import CharlyAuth

auth = CharlyAuth(
    base_url="https://app.charly.io/api/v1",
    timeout=30
)

api_key = auth.create_session(
    username="usuario@ejemplo.com",
    password="contraseña_segura"
)

print(f"API Key obtenida: {api_key}")
```

### Usando Bootstrap (Flujo Completo)

```python
from pathlib import Path
from orchestration.bootstrap import Bootstrap

ctx = Bootstrap(
    config_path=Path("config/charly.yaml")
).run()

api_key = ctx["api_key"]
client = ctx["client"]
```

### Request HTTP Directo

```python
import json
import urllib.request

url = "https://app.charly.io/api/v1/sessions"

payload = {
    "username": "usuario@ejemplo.com",
    "password": "contraseña_segura"
}

data = json.dumps(payload).encode("utf-8")

request = urllib.request.Request(
    url=url,
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(request, timeout=30) as response:
    body = json.loads(response.read().decode("utf-8"))
    api_key = body["api_key"]
```

---

## Manejo de Errores

### 401 Unauthorized

Credenciales inválidas o usuario no existe.

```json
{
    "error": "Invalid credentials"
}
```

**Ejemplo de manejo:**

```python
from core.auth import CharlyAuth
from core.exceptions import AuthError

try:
    auth = CharlyAuth(base_url="https://app.charly.io/api/v1")
    api_key = auth.create_session("usuario@ejemplo.com", "password")
except AuthError as e:
    print(f"Error de autenticación: {e.message}")
    print(f"Status: {e.status_code}")
```

### 400 Bad Request

Request mal formado (JSON inválido, campos faltantes).

### 500 Internal Server Error

Error del servidor de Charly.io.

---

## Persistencia de API Key

El sistema guarda automáticamente la API key obtenida para evitar múltiples autenticaciones:

**Ubicación:** `_charly_secrets/api_keys.json`

**Formato:**
```json
{
    "usuario_sistema": "api_key_obtenida"
}
```

**Implementación:**
```python
from security.api_key_store import ApiKeyStore
from security.paths import get_api_key_store_path

api_key_store = ApiKeyStore(get_api_key_store_path())
api_key_store.save("usuario_sistema", api_key)
```

---

## Flujo de Autenticación Completo

```
┌─────────────────────────────────────────┐
│  1. Resolver usuario del sistema       │
└───────────────┬───────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  2. Cargar credenciales desde           │
│     _charly_secrets/charly_users.json   │
└───────────────┬───────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  3. POST /sessions                      │
│     {username, password}                 │
└───────────────┬───────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  4. Obtener api_key de la respuesta     │
└───────────────┬───────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  5. Guardar api_key en                  │
│     _charly_secrets/api_keys.json       │
└───────────────┬───────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  6. Crear CharlyApiClient con api_key   │
└─────────────────────────────────────────┘
```

---

## Notas Importantes

1. **Seguridad:**
   - ⚠️ Nunca commitees credenciales al repositorio
   - Los archivos `_charly_secrets/` están en `.gitignore`
   - La API key tiene un tiempo de expiración (verificar con Charly.io)

2. **Rate Limiting:**
   - Este endpoint puede tener límites de rate limiting
   - Evitar múltiples intentos de autenticación en corto tiempo

3. **Reutilización:**
   - La API key puede reutilizarse para múltiples requests
   - El sistema intenta cargar API keys cacheadas antes de autenticar

4. **Timeout:**
   - Timeout recomendado: 30 segundos
   - El sistema usa timeout configurable desde `config/charly.yaml`

---

## Casos de Uso

### Caso 1: Autenticación Inicial

```python
from core.auth import CharlyAuth

auth = CharlyAuth(base_url="https://app.charly.io/api/v1")
api_key = auth.create_session("usuario@ejemplo.com", "password")
# Usar api_key para crear cliente
```

### Caso 2: Renovación de API Key

```python
from security.api_key_store import ApiKeyStore
from security.paths import get_api_key_store_path
from core.auth import CharlyAuth

# Verificar si hay API key cacheada
api_key_store = ApiKeyStore(get_api_key_store_path())
cached_key = api_key_store.get("usuario_sistema")

if not cached_key:
    # Renovar autenticación
    auth = CharlyAuth(base_url="https://app.charly.io/api/v1")
    api_key = auth.create_session("usuario@ejemplo.com", "password")
    api_key_store.save("usuario_sistema", api_key)
```

---

## Referencias

- **Implementación:** `core/auth.py` - Clase `CharlyAuth`
- **Bootstrap:** `orchestration/bootstrap.py` - Método `_login()`
- **Almacenamiento:** `security/api_key_store.py` - Clase `ApiKeyStore`
