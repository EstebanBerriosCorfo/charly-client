"""
==============================================================================
⚠️ IMPORTANTE — INTERPRETACIÓN DEL RESPONSE DE /companies
==============================================================================

El endpoint GET /companies de la API de Charly NO devuelve "empresas"
en el sentido jurídico tradicional (razón social, RUT, etc.).

En el dominio de Charly:

    "Company" = ACTOR POSTULANTE

Es decir, representa a quien postula a un programa dentro de una organización,
y puede corresponder a:

    - Personas naturales
    - Emprendimientos individuales
    - Consultores
    - Empresas formales (SpA, EIRL, Ltda), cuando existen

Por esta razón, el response puede incluir registros con:

    - first_name / last_name (persona natural)
    - name como nombre de fantasía o nombre personal
    - fantasy_name = None
    - employee_size = "xs"
    - email personal (gmail, hotmail, etc.)
    - ausencia de datos jurídicos formales

Esto es ESPERADO, especialmente en organizaciones como:

    - Corfo Innova - Certificación Ley I+D (organization_id = 162)

donde está permitida la postulación de personas naturales y micro actores.

❗ NO asumir que "company" == empresa CORFO formal.

La distinción jurídica real (empresa vs persona) suele aparecer recién
en capas posteriores del modelo (postulaciones, programas, integraciones CORFO).

Este script devuelve correctamente lo que expone la API de Charly,
aunque el modelo semántico pueda resultar contraintuitivo.
==============================================================================
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
# Imports
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
# SELECCIÓN DE ORGANIZACIÓN
# ------------------------------------------------------------------
organizations = org_service.list()

print("\n=== ORGANIZATIONS DISPONIBLES ===")
for org in organizations:
    print(f"- ID: {org['id']} | Nombre: {org['name']}")

org_id_input = input("\nIngrese el ID de la organización: ").strip()

if not org_id_input.isdigit():
    print("❌ ID de organización inválido")
    sys.exit(1)

organization_id = int(org_id_input)

# ------------------------------------------------------------------
# LISTAR COMPANIES
# ------------------------------------------------------------------
payload = company_service.list_companies(organization_id)

print(f"\n=== COMPANIES (ORG {organization_id}) ===")
print(f"Total: {payload.get('count')}")
pprint(payload.get("results", []))
