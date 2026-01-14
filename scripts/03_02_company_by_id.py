"""
────────────────────────────────────────────────────────────────────────────
📌 EXPLICACIÓN DEL COMPORTAMIENTO DEL ENDPOINT /companies/{company_id}
────────────────────────────────────────────────────────────────────────────

Este script implementa la consulta del endpoint:

    GET /companies/{company_id}?api_key=API_KEY&organization_id=ORGANIZATION_ID

De acuerdo al contrato oficial de la API de Charly, este endpoint permite
obtener el detalle de una empresa específica (company), siempre en el
contexto de una organización.

────────────────────────────────────────────────────────────────────────────
🔎 ACLARACIÓN CONCEPTUAL IMPORTANTE
────────────────────────────────────────────────────────────────────────────

En Charly, el recurso "Company" NO representa exclusivamente una empresa
formal (persona jurídica), sino un ACTOR POSTULANTE dentro de una organización.

Por esta razón, el listado y el detalle de companies puede incluir:

- Personas naturales (emprendedores individuales)
- Personas jurídicas (SpA, EIRL, Ltda, etc.)
- Registros de uso personal o administrativos (ej: "NO OCUPAR")
- Empresas con nombre comercial
- Empresas cuyo nombre coincide con el nombre de una persona

Esto explica por qué en el response aparecen campos como:

- first_name
- last_name
- email personal
- employee_size = "xs"

y nombres que parecen personas, no empresas tradicionales.

────────────────────────────────────────────────────────────────────────────
🧩 RELACIÓN ORGANIZATION → COMPANIES
────────────────────────────────────────────────────────────────────────────

Cuando se consulta:

    GET /companies?organization_id=162

(Organización: Corfo Innova - Certificación Ley I+D)

La API devuelve TODAS las companies (actores postulantes) que han interactuado
con esa organización, independiente de si corresponden a:

- Proyectos Ley I+D
- Postulaciones individuales
- Empresas proveedoras
- Registros históricos

Por lo tanto:
✔ El volumen alto de resultados es esperado
✔ El contenido heterogéneo del response es correcto
✔ El endpoint está funcionando según diseño de la API

────────────────────────────────────────────────────────────────────────────
📄 RESPONSE DEL ENDPOINT /companies/{company_id}
────────────────────────────────────────────────────────────────────────────

Aunque el contrato documentado muestra un response mínimo:

    {
      "id": 1,
      "name": "VC 1"
    }

En la práctica, Charly devuelve un payload extendido con metadata adicional,
como:

- Datos de contacto
- Información de tamaño
- URLs
- Fechas de creación / actualización

Este comportamiento es consistente en toda la API y debe ser tratado como
válido.

────────────────────────────────────────────────────────────────────────────
✅ CONCLUSIÓN
────────────────────────────────────────────────────────────────────────────

El response observado en este script es:
- Correcto
- Esperado
- Alineado con el modelo real de datos de Charly

Cualquier filtrado, normalización o interpretación de estos datos debe
realizarse en capas posteriores (servicios de negocio, ETL, reporting, etc.),
NO en la capa de acceso a la API.

────────────────────────────────────────────────────────────────────────────
"""

import sys
from pathlib import Path
from pprint import pprint

# ------------------------------------------------------------------
# Ajuste de path del proyecto
# ------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ------------------------------------------------------------------
# Imports del sistema
# ------------------------------------------------------------------
from orchestration.bootstrap import Bootstrap
from services.organization_service import OrganizationService
from services.company_service import CompanyService

# ------------------------------------------------------------------
# BOOTSTRAP
# ------------------------------------------------------------------
ctx = Bootstrap(
    config_path=Path("config/charly.yaml")
).run()

client = ctx["client"]

org_service = OrganizationService(client)
company_service = CompanyService(client)

# ------------------------------------------------------------------
# LISTAR ORGANIZACIONES DISPONIBLES
# ------------------------------------------------------------------
orgs_payload = org_service.list_organizations()
organizations = orgs_payload.get("results", [])

print("\n=== ORGANIZACIONES DISPONIBLES ===")
for org in organizations:
    print(f"- ID: {org['id']} | Nombre: {org['name']}")

# ------------------------------------------------------------------
# INPUT ORGANIZATION_ID
# ------------------------------------------------------------------
org_id_input = input("\nIngrese el ID de la organización: ").strip()

if not org_id_input.isdigit():
    raise ValueError("El organization_id debe ser un número entero.")

organization_id = int(org_id_input)

# ------------------------------------------------------------------
# LISTAR COMPANIES DE LA ORGANIZACIÓN
# ------------------------------------------------------------------
companies_payload = company_service.list_companies(organization_id)
companies = companies_payload.get("results", [])

print("\n=== COMPANIES DISPONIBLES EN LA ORGANIZACIÓN ===")
for company in companies:
    print(f"- ID: {company['id']} | Nombre: {company.get('name')}")

# ------------------------------------------------------------------
# INPUT COMPANY_ID
# ------------------------------------------------------------------
company_id_input = input("\nIngrese el ID de la company a consultar: ").strip()

if not company_id_input.isdigit():
    raise ValueError("El company_id debe ser un número entero.")

company_id = int(company_id_input)

# ------------------------------------------------------------------
# CONSULTA DETALLE DE COMPANY
# ------------------------------------------------------------------
company_detail = company_service.get_company(
    company_id=company_id,
    organization_id=organization_id
)

print("\n=== COMPANY (DETALLE) ===")
pprint(company_detail)
