# ================================================================
# Script 05_01_03_generate_applications_excel.py
#
# Orquestador principal para generar el Excel de postulaciones
# de una convocatoria específica.
#
# Flujo:
#   1. Bootstrap Charly
#   2. Selección de convocatoria (program)
#   3. Descarga postulaciones completas (include_data=true)
#   4. Normalización a DataFrame
#   5. Exportación a Excel (downloads/)
#
# Resultado:
#   Archivo Excel equivalente al descargable oficial de Charly
# ================================================================

import sys
from pathlib import Path

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
from utils.dataframe_builder import build_applications_dataframe
from utils.excel_exporter import export_applications_dataframe_to_excel
from security.paths import get_project_root


# ------------------------------------------------------------------
# RUTA DE DESCARGA
# ------------------------------------------------------------------
DOWNLOADS_DIR = get_project_root() / "downloads"
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------
# BOOTSTRAP
# ------------------------------------------------------------------
ctx = Bootstrap(
    config_path=Path("config/charly.yaml")
).run()

client: CharlyApiClient = ctx["client"]
program_service = ProgramService(client)

# ------------------------------------------------------------------
# LISTAR PROGRAMAS
# ------------------------------------------------------------------
print("\n=== PROGRAMAS DISPONIBLES ===")
programs_payload = program_service.list_programs()
programs = programs_payload.get("results", [])

for p in programs:
    print(
        f"- ID: {p['id']} | "
        f"Nombre: {p['name']} | "
        f"Org ID: {p['organization_id']} | "
        f"Estado: {p['application_status']}"
    )

# ------------------------------------------------------------------
# INPUT USUARIO
# ------------------------------------------------------------------
program_id = input("\nIngrese el ID del programa: ").strip()

if not program_id.isdigit():
    raise ValueError("El program_id debe ser numérico")

program_id = int(program_id)

program = next(
    (p for p in programs if p["id"] == program_id),
    None
)

if program is None:
    print(
        f"\n⚠️ El programa {program_id} no apareció en el listado inicial.\n"
        "Se continuará igual usando el program_id ingresado."
    )
    program_name = f"program_{program_id}"
else:
    program_name = program["name"]


print(f"\n▶ Programa seleccionado: {program_name}")

# ------------------------------------------------------------------
# DESCARGA DE POSTULACIONES COMPLETAS
# ------------------------------------------------------------------
print("\n▶ Obteniendo convocatoria con todas las postulaciones...")

program_payload = client.request(
    method="GET",
    endpoint=f"/programs/{program_id}"
)

applications = program_payload.get("applications", [])

print(f"✔ Total postulaciones encontradas: {len(applications)}")

if not applications:
    raise RuntimeError(
        f"La convocatoria {program_id} no devolvió postulaciones, "
        "pero la UI indica que sí existen."
    )

# ------------------------------------------------------------------
# CONSTRUCCIÓN DATAFRAME
# ------------------------------------------------------------------
print("\n▶ Construyendo DataFrame normalizado...")

df = build_applications_dataframe(applications)

print(f"✔ DataFrame listo | Filas: {df.shape[0]} | Columnas: {df.shape[1]}")

# ------------------------------------------------------------------
# EXPORTACIÓN A EXCEL
# ------------------------------------------------------------------
safe_program_name = (
    program_name
    .replace(" ", "_")
    .replace("/", "-")
    .replace("–", "-")
)

output_file = DOWNLOADS_DIR / f"applications_{program_id}_{safe_program_name}.xlsx"

print("\n▶ Exportando a Excel...")
export_applications_dataframe_to_excel(
    df=df,
    output_path=output_file
)

print("\n✅ EXCEL GENERADO CORRECTAMENTE")
print(f"📁 Ruta: {output_file}")
