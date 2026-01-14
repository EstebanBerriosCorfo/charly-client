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

# ------------------------------------------------------------------
# BOOTSTRAP
# ------------------------------------------------------------------
ctx = Bootstrap(
    config_path=Path("config/charly.yaml")
).run()

client = ctx["client"]
service = OrganizationService(client)

# ------------------------------------------------------------------
# LISTAR ORGANIZACIONES DISPONIBLES
# ------------------------------------------------------------------
organizations = service.list()

print("\n=== ORGANIZATIONS DISPONIBLES ===")
for org in organizations:
    print(f"- ID: {org['id']} | Nombre: {org['name']}")

# ------------------------------------------------------------------
# INPUT DEL USUARIO
# ------------------------------------------------------------------
organization_id_input = input(
    "\nIngrese el ID de la organización a consultar: "
).strip()

if not organization_id_input:
    print("❌ No se ingresó ningún ID. Abortando.")
    sys.exit(1)

if not organization_id_input.isdigit():
    print("❌ El ID debe ser numérico. Abortando.")
    sys.exit(1)

organization_id = int(organization_id_input)

# ------------------------------------------------------------------
# CONSULTA ORGANIZACIÓN POR ID
# ------------------------------------------------------------------
organization = service.get_by_id(organization_id)

print(f"\n=== ORGANIZATION BY ID ({organization_id}) ===")
pprint(organization)
