# ================================================================
# Script 05_01_applications_by_program_full.py
#
# Objetivo:
#   Obtener TODAS las postulaciones de una convocatoria (program)
#   incluyendo:
#     - Metadata de la postulación
#     - Empresa
#     - Formularios
#     - Preguntas
#     - Respuestas
#     - Evaluaciones
#
# Endpoint utilizado (FUENTE DEL EXCEL REAL):
#   GET /applications?program_id=XXX&include_data=true
#
# Este script NO transforma datos.
# Solo extrae la fuente canónica.
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
from core.client import CharlyApiClient
from services.program_service import ProgramService

# ------------------------------------------------------------------
# BOOTSTRAP
# ------------------------------------------------------------------
ctx = Bootstrap(
    config_path=Path("config/charly.yaml")
).run()

client: CharlyApiClient = ctx["client"]
program_service = ProgramService(client)

# ------------------------------------------------------------------
# LISTAR PROGRAMAS DISPONIBLES (UX HUMANO)
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
# CONSULTA CANÓNICA DE POSTULACIONES (EXCEL REAL)
# ------------------------------------------------------------------
print("\n▶ Obteniendo postulaciones completas (include_data=true)...")

applications_payload = client.request(
    method="GET",
    endpoint="/applications",
    params={
        "program_id": program_id,
        "include_data": "true"
    }
)

applications = applications_payload.get("results", [])

print(f"✔ Total postulaciones encontradas: {len(applications)}")

# ------------------------------------------------------------------
# OUTPUT JSON COMPLETO (1 POSTULACIÓN = 1 BLOQUE)
# ------------------------------------------------------------------
print("\n=== POSTULACIONES (JSON COMPLETO POR POSTULACIÓN) ===")

for idx, application in enumerate(applications, start=1):
    print(f"\n--- POSTULACIÓN #{idx} ---")
    pprint(application, width=140)