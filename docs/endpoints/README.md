# Documentación de Endpoints - API Charly.io

Esta carpeta contiene la documentación detallada de cada endpoint de la API de Charly.io.

**📋 Convención de Numeración:** Los números de los documentos siguen la convención de los scripts en `scripts/`, indicando que el comportamiento del endpoint está implementado y documentado. Si un endpoint tiene un script correspondiente, se indica en la documentación.

---

## Índice de Endpoints

La numeración de los documentos sigue la convención de los scripts en `scripts/`, indicando que el comportamiento del endpoint está implementado y documentado.

### Autenticación

- **[00_POST_sessions](00_POST_sessions.md)** - Crear sesión y obtener API key
  - Autenticación inicial
  - Único endpoint que NO requiere API key
  - Retorna `api_key` para requests posteriores
  - **Script:** `00_bootstrap.py` (incluido en bootstrap)

### Usuario

- **[01_GET_current_user](01_GET_current_user.md)** - Obtener información del usuario activo
  - Validar autenticación
  - Obtener empresas y organizaciones asociadas
  - Validación de entorno
  - **Script:** `01_current_user.py`

### Organizaciones

- **[02_01_GET_organizations](02_01_GET_organizations.md)** - Listar organizaciones
  - Listado paginado de todas las organizaciones
  - Filtros disponibles
  - **Script:** `02_01_organizations.py`

- **[02_02_GET_organizations_by_id](02_02_GET_organizations_by_id.md)** - Obtener organización específica
  - Detalle completo de una organización
  - Información adicional (descripción, website, settings)
  - **Script:** `02_02_organization_by_id.py`

### Empresas

- **[03_01_GET_companies](03_01_GET_companies.md)** - Listar empresas por organización
  - Listado paginado de empresas
  - ⚠️ "Company" = Actor postulante (puede ser persona natural o empresa formal)
  - **Script:** `03_01_companies.py`

- **[03_02_GET_companies_by_id](03_02_GET_companies_by_id.md)** - Obtener empresa específica
  - Detalle completo de una empresa
  - Información fiscal, dirección, metadata
  - **Script:** `03_02_company_by_id.py`

### Convocatorias (Programs)

- **[04_01_GET_programs](04_01_GET_programs.md)** - Listar convocatorias
  - Listado paginado con filtros
  - Filtros: organización, estado de postulación, estado de evaluación, fecha
  - **Script:** `04_01_programs.py`

- **[04_02_GET_programs_by_id](04_02_GET_programs_by_id.md)** - Obtener convocatoria con postulaciones
  - Detalle completo de una convocatoria
  - **Incluye todas las postulaciones asociadas**
  - Filtro por estado de postulación de empresa
  - **Scripts:** `04_02_programs_by_id.py`, `05_00_program_applications_index.py`

### Postulaciones (Applications)

- **[05_01_GET_applications](05_01_GET_applications.md)** - Listar postulaciones
  - Listado paginado con filtros temporales
  - Filtros: fechas, IDs específicos
  - ⚠️ `include_data=true` es costoso (incluye respuestas completas)
  - **Script:** `05_01_applications.py`

- **[05_02_GET_applications_by_id](05_02_GET_applications_by_id.md)** - Obtener postulación completa
  - Detalle completo de una postulación
  - **Incluye todas las respuestas (form_answers y field_answers)**
  - Incluye evaluaciones
  - **Script:** No hay script directo (usado en orquestación)

### KPIs y Métricas

- **[06_01_GET_mgr_fields](06_01_GET_mgr_fields.md)** - Listar KPIs por organización
  - Listado paginado de KPIs
  - Metadata de campos/métricas
  - **Script:** `06_kpis.py`

- **[06_02_GET_mgr_fields_by_id](06_02_GET_mgr_fields_by_id.md)** - Obtener KPI con data agregada
  - Detalle completo de un KPI
  - **Incluye data agregada (series, distribuciones)**
  - Formato compatible con gráficos (Chart.js)
  - **Script:** No hay script directo (usado en orquestación)

---

## Estructura de Documentación

Cada documento incluye:

- ✅ **Descripción** del endpoint
- ✅ **Especificación técnica** (método, path, autenticación, paginación)
- ✅ **Request** (parámetros, ejemplos)
- ✅ **Response** (estructura, campos, ejemplos)
- ✅ **Ejemplos de uso** (con servicios, HTTP directo)
- ✅ **Filtros disponibles**
- ✅ **Paginación** (si aplica)
- ✅ **Manejo de errores**
- ✅ **Casos de uso** prácticos
- ✅ **Notas importantes**
- ✅ **Referencias** a implementación y scripts

---

## Flujo Recomendado de Uso

### 1. Autenticación
```
POST /sessions → obtener api_key
```

### 2. Validación
```
GET /current_user → validar entorno
```

### 3. Navegación Jerárquica
```
GET /organizations → obtener organizaciones
GET /programs?organization_id=X → obtener convocatorias
GET /programs/{id} → obtener convocatoria con postulaciones
GET /applications/{id} → obtener postulación completa
```

### 4. Análisis de KPIs
```
GET /mgr/fields?organization_id=X → listar KPIs
GET /mgr/fields/{id}?organization_id=X → obtener KPI con data
```

---

## Endpoints por Categoría

### Endpoints de Autenticación
- `POST /sessions`

### Endpoints de Consulta (GET)
- `GET /current_user` → [01_GET_current_user.md](01_GET_current_user.md)
- `GET /organizations` → [02_01_GET_organizations.md](02_01_GET_organizations.md)
- `GET /organizations/{id}` → [02_02_GET_organizations_by_id.md](02_02_GET_organizations_by_id.md)
- `GET /companies` → [03_01_GET_companies.md](03_01_GET_companies.md)
- `GET /companies/{id}` → [03_02_GET_companies_by_id.md](03_02_GET_companies_by_id.md)
- `GET /programs` → [04_01_GET_programs.md](04_01_GET_programs.md)
- `GET /programs/{id}` → [04_02_GET_programs_by_id.md](04_02_GET_programs_by_id.md)
- `GET /applications` → [05_01_GET_applications.md](05_01_GET_applications.md)
- `GET /applications/{id}` → [05_02_GET_applications_by_id.md](05_02_GET_applications_by_id.md)
- `GET /mgr/fields` → [06_01_GET_mgr_fields.md](06_01_GET_mgr_fields.md)
- `GET /mgr/fields/{id}` → [06_02_GET_mgr_fields_by_id.md](06_02_GET_mgr_fields_by_id.md)

### Endpoints Paginados
- `GET /organizations` → [02_01_GET_organizations.md](02_01_GET_organizations.md)
- `GET /companies` → [03_01_GET_companies.md](03_01_GET_companies.md)
- `GET /programs` → [04_01_GET_programs.md](04_01_GET_programs.md)
- `GET /applications` → [05_01_GET_applications.md](05_01_GET_applications.md)
- `GET /mgr/fields` → [06_01_GET_mgr_fields.md](06_01_GET_mgr_fields.md)

### Endpoints con Data Completa
- `GET /programs/{id}` → [04_02_GET_programs_by_id.md](04_02_GET_programs_by_id.md) - Incluye applications
- `GET /applications/{id}` → [05_02_GET_applications_by_id.md](05_02_GET_applications_by_id.md) - Incluye form_answers y field_answers
- `GET /mgr/fields/{id}` → [06_02_GET_mgr_fields_by_id.md](06_02_GET_mgr_fields_by_id.md) - Incluye data agregada

---

## Notas Generales

### Autenticación
- Todos los endpoints (excepto `/sessions`) requieren `api_key`
- La API key se obtiene de `POST /sessions`
- La API key se inyecta automáticamente por `CharlyApiClient`

### Paginación
- Los endpoints paginados retornan formato estándar:
  ```json
  {
    "count": 100,
    "previous": null,
    "next": "url",
    "results": [...]
  }
  ```
- Usar métodos `iterate_*()` de los servicios para paginación automática

### Rate Limiting
- El sistema maneja automáticamente rate limiting con backoff exponencial
- Ver `utils/rate_limit.py` para detalles

### Normalización
- Usar normalizadores para convertir JSON anidado a tablas planas:
  - `ApplicationNormalizer` para applications
  - `KPINormalizer` para KPIs

---

## Referencias Generales

- **Flujo Completo:** Ver `FLUJO_CONSUMO_API.md` en la raíz del proyecto
- **Implementación:** Ver `services/` para servicios de cada endpoint
- **Ejemplos:** Ver `scripts/` para scripts de ejemplo
- **Configuración:** Ver `config/charly.yaml`

---

## Convenciones de Nomenclatura

- **Programs** = Convocatorias
- **Applications** = Postulaciones
- **Companies** = Actores postulantes (puede ser persona natural o empresa formal)
- **Fields** = KPIs / Campos / Métricas
- **Form Answers** = Respuestas a formularios
- **Field Answers** = Respuestas a campos específicos

---

Última actualización: Enero 2025
 