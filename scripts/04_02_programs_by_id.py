# scripts/04_02_programs_by_id.py
# ================================================================
# Consulta de Convocatoria por ID
# - Obtiene el detalle del programa
# - Muestra todas las postulaciones asociadas
# - Imprime cada postulación como JSON completo (una por fila)
#
# Este script está diseñado para:
# - Validar el contrato real de la API
# - Servir como fuente de verdad del modelo de datos
# - Facilitar diseño posterior de ETL / snapshots / BI
#
# NO se realizan transformaciones de datos en esta etapa.
# ================================================================

import sys
import json
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
from services.program_service import ProgramService

# ------------------------------------------------------------------
# BOOTSTRAP
# ------------------------------------------------------------------
ctx = Bootstrap(
    config_path=Path("config/charly.yaml")
).run()

client = ctx["client"]

org_service = OrganizationService(client)
program_service = ProgramService(client)

# ------------------------------------------------------------------
# LISTAR ORGANIZACIONES
# ------------------------------------------------------------------
organizations = org_service.list()

print("\n=== ORGANIZACIONES DISPONIBLES ===")
for org in organizations:
    print(f"- ID: {org['id']} | Nombre: {org['name']}")

organization_id = int(input("\nIngrese el ID de la organización: ").strip())

# ------------------------------------------------------------------
# LISTAR PROGRAMAS DE LA ORGANIZACIÓN
# ------------------------------------------------------------------
programs = program_service.iterate_programs(
    organization_id=organization_id
)

print("\n=== PROGRAMAS DISPONIBLES ===")
for program in programs:
    print(
        f"- ID: {program['id']} | "
        f"Nombre: {program['name']} | "
        f"Org ID: {program['organization_id']} | "
        f"Estado postulación: {program['application_status']}"
    )

program_id = int(input("\nIngrese el ID del programa a consultar: ").strip())

# ------------------------------------------------------------------
# DETALLE DE PROGRAMA + POSTULACIONES
# ------------------------------------------------------------------
program_detail = program_service.get_program(program_id)

print("\n=== PROGRAMA (DETALLE) ===")
pprint({k: v for k, v in program_detail.items() if k != "applications"})

# ------------------------------------------------------------------
# POSTULACIONES (JSON PURO POR FILA)
# ------------------------------------------------------------------
applications = program_detail.get("applications", [])

print("\n=== POSTULACIONES (FORMATO JSON POR FILA) ===")
print(f"Total postulaciones encontradas: {len(applications)}\n")

if not applications:
    print("⚠️  Esta convocatoria no tiene postulaciones registradas.")
else:
    for idx, application in enumerate(applications, start=1):
        print(f"--- POSTULACIÓN {idx} ---")
        print(json.dumps(application, indent=2, ensure_ascii=False))
        print()
