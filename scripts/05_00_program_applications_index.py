# ================================================================
# Script 05_00_program_applications_index.py
#
# Objetivo:
#   Obtener el ÍNDICE de postulaciones de una convocatoria (program),
#   incluyendo:
#     - Estado general del programa
#     - Metadata del programa
#     - Listado de postulaciones (applications)
#     - Estados de cada postulación
#     - Empresa asociada
#     - Scores y contadores
#
# Endpoint utilizado:
#   GET /programs/{program_id}
#
# IMPORTANTE:
#   ❌ Este endpoint NO trae respuestas de formularios
#   ✅ Se usa para control, trazabilidad y validación previa
# ================================================================

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
from core.client import CharlyApiClient

# ------------------------------------------------------------------
# BOOTSTRAP
# ------------------------------------------------------------------
ctx = Bootstrap(
    config_path=Path("config/charly.yaml")
).run()

client: CharlyApiClient = ctx["client"]
program_service = ProgramService(client)

# ------------------------------------------------------------------
# LISTAR PROGRAMAS DISPONIBLES (UX)
# ------------------------------------------------------------------
print("\n=== PROGRAMAS DISPONIBLES ===")
programs_payload = program_service.list_programs()
programs = programs_payload.get("results", [])

for p in programs:
    print(
        f"- ID: {p['id']} | "
        f"Nombre: {p['name']} | "
        f"Org ID: {p['organization_id']} | "
        f"Estado postulación: {p['application_status']}"
    )

# ------------------------------------------------------------------
# INPUT USUARIO
# ------------------------------------------------------------------
program_id = input("\nIngrese el ID del programa a consultar: ").strip()

if not program_id.isdigit():
    raise ValueError("❌ El program_id debe ser numérico")

program_id = int(program_id)

# ------------------------------------------------------------------
# CONSULTA ÍNDICE DE POSTULACIONES
# ------------------------------------------------------------------
print("\n▶ Obteniendo índice de postulaciones del programa...")

program_detail = program_service.get_program(program_id)

# ------------------------------------------------------------------
# OUTPUT CONTROLADO
# ------------------------------------------------------------------
print("\n=== METADATA DEL PROGRAMA ===")
pprint(
    {
        "program_id": program_detail.get("id"),
        "name": program_detail.get("name"),
        "organization_id": program_detail.get("organization_id"),
        "application_status": program_detail.get("application_status"),
        "evaluation_status": program_detail.get("evaluation_status"),
        "deadline": program_detail.get("deadline"),
        "start_date": program_detail.get("start_date"),
    },
    width=120
)

applications = program_detail.get("applications", [])

print(f"\n✔ Total postulaciones indexadas: {len(applications)}")

print("\n=== POSTULACIONES (ÍNDICE / CONTROL) ===")
for idx, app in enumerate(applications, start=1):
    print(
        f"{idx:03d} | "
        f"App ID: {app.get('id')} | "
        f"Empresa: {app.get('company', {}).get('name')} | "
        f"Estado: {app.get('application_status')} | "
        f"Estado empresa: {app.get('company_application_status')} | "
        f"Formularios: {app.get('form_answers_count')} | "
        f"Score Eval: {app.get('score_eval')}"
    )
