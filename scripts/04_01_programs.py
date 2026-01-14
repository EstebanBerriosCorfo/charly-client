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
from services.program_service import ProgramService

# ------------------------------------------------------------------
# BOOTSTRAP
# ------------------------------------------------------------------
ctx = Bootstrap(
    config_path=Path("config/charly.yaml")
).run()

client = ctx["client"]
program_service = ProgramService(client)

# ------------------------------------------------------------------
# INPUT DE FILTROS (opcionales)
# ------------------------------------------------------------------
print("\n=== FILTROS DE CONSULTA (opcional) ===")
org_id = input("Organization ID (Enter para omitir): ").strip()
application_status = input("Application status [draft/open/finished] (Enter para omitir): ").strip()
evaluation_status = input("Evaluation status [draft/open/finished] (Enter para omitir): ").strip()
created_at = input("Created at desde (YYYY-MM-DD) (Enter para omitir): ").strip()

filters = {}

if org_id:
    filters["organization_id"] = int(org_id)

if application_status:
    filters["application_status"] = application_status

if evaluation_status:
    filters["evaluation_status"] = evaluation_status

if created_at:
    filters["created_at"] = created_at

# ------------------------------------------------------------------
# CONSULTA A API
# ------------------------------------------------------------------
response = program_service.list_programs(**filters)

programs = response.get("results", [])

# ------------------------------------------------------------------
# OUTPUT
# ------------------------------------------------------------------
print("\n=== PROGRAMS / CONVOCATORIAS ===")
print(f"Total encontrados: {response.get('count', 0)}\n")

for program in programs:
    print(
        f"- ID: {program['id']} | "
        f"Nombre: {program['name']} | "
        f"Org: {program['organization_id']} | "
        f"Postulación: {program['application_status']} | "
        f"Evaluación: {program['evaluation_status']}"
    )

# ------------------------------------------------------------------
# DEBUG OPCIONAL
# ------------------------------------------------------------------
# pprint(programs)
