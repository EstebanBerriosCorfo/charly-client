# scripts/05_01_applications.py
# ================================================================
# Consulta de Postulaciones (Applications)
# Endpoint: GET /applications
#
# Objetivo:
#   - Listar postulaciones con filtros temporales y de IDs
#   - Opción de incluir datos completos (include_data)
#   - Mostrar metadata básica de las postulaciones
#
# Filtros disponibles:
#   - start_date: fecha mínima (YYYY-MM-DD)
#   - end_date: fecha máxima (YYYY-MM-DD)
#   - date_type: created_at | updated_at (default: created_at)
#   - ids: lista de IDs específicos (separados por coma)
#   - include_data: true para incluir respuestas completas (costoso)
#
# ⚠️ IMPORTANTE:
#   - include_data=true es muy costoso para grandes volúmenes
#   - Usar filtros de fecha para limitar el volumen
#   - Para respuestas completas, considerar períodos cortos
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
from services.application_service import ApplicationService

# ------------------------------------------------------------------
# BOOTSTRAP
# ------------------------------------------------------------------
ctx = Bootstrap(
    config_path=Path("config/charly.yaml")
).run()

client = ctx["client"]
application_service = ApplicationService(client)

# ------------------------------------------------------------------
# INPUT DE FILTROS (opcionales)
# ------------------------------------------------------------------
print("\n=== FILTROS DE CONSULTA (opcional) ===")
start_date = input("Fecha inicio (YYYY-MM-DD) (Enter para omitir): ").strip()
end_date = input("Fecha fin (YYYY-MM-DD) (Enter para omitir): ").strip()
date_type = input("Tipo de fecha [created_at/updated_at] (Enter para created_at): ").strip()
ids_input = input("IDs de postulaciones (application_id) separados por coma (ej: 123,456,789) (Enter para omitir): ").strip()
include_data = input("Incluir datos completos (respuestas) [y/N] (costoso): ").strip().lower()

filters = {}

if start_date:
    filters["start_date"] = start_date

if end_date:
    filters["end_date"] = end_date

if date_type:
    filters["date_type"] = date_type
else:
    filters["date_type"] = "created_at"  # Default

if ids_input:
    try:
        ids_list = [int(id_str.strip()) for id_str in ids_input.split(",")]
        filters["ids"] = ids_list
    except ValueError:
        print("⚠️  Error: Los IDs de postulaciones deben ser números separados por coma. Ignorando filtro de IDs.")

if include_data == "y":
    # Validar que se proporcionen filtros de fecha o IDs cuando include_data=True
    if not filters.get("start_date") and not filters.get("end_date") and not filters.get("ids"):
        print("\n❌ ERROR: include_data=True requiere filtros de fecha o IDs específicos.")
        print("   Sin filtros, el request puede causar timeout al intentar obtener todas las postulaciones.")
        print("   Por favor, proporciona al menos:")
        print("   - Fecha inicio y/o fecha fin, O")
        print("   - IDs de postulaciones (application_id) específicos")
        sys.exit(1)
    
    filters["include_data"] = True
    print("\n⚠️  ADVERTENCIA: include_data=True puede hacer el request muy lento para grandes volúmenes")
    if not filters.get("ids"):
        print("   Se recomienda usar períodos cortos (máximo 1 mes) para evitar timeouts.")
else:
    filters["include_data"] = False

# ------------------------------------------------------------------
# CONSULTA A API
# ------------------------------------------------------------------
try:
    response = application_service.list_applications(**filters)
    applications = response.get("results", [])
except Exception as e:
    error_msg = str(e)
    if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
        print("\n❌ ERROR: Timeout al consultar el endpoint.")
        print("   Posibles causas:")
        print("   1. include_data=True sin filtros de fecha adecuados")
        print("   2. Rango de fechas muy amplio con include_data=True")
        print("   3. Problemas de conectividad")
        print("\n   Soluciones:")
        print("   - Usar filtros de fecha más específicos")
        print("   - Reducir el rango de fechas (máximo 1 mes con include_data=True)")
        print("   - Usar IDs de postulaciones (application_id) específicos en lugar de rango de fechas")
        print("   - Desactivar include_data para obtener solo metadata")
    else:
        print(f"\n❌ ERROR al consultar el endpoint: {error_msg}")
    sys.exit(1)

# ------------------------------------------------------------------
# OUTPUT
# ------------------------------------------------------------------
print("\n=== APPLICATIONS / POSTULACIONES ===")
print(f"Total encontradas: {response.get('count', 0)}\n")

for application in applications:
    company = application.get("company", {})
    company_name = company.get("name", "N/A") if company else "N/A"
    
    print(
        f"- ID: {application.get('id')} | "
        f"Nombre: {application.get('name', 'N/A')} | "
        f"Programa ID: {application.get('program_id')} | "
        f"Empresa: {company_name} | "
        f"Estado: {application.get('application_status', 'N/A')} | "
        f"Estado empresa: {application.get('company_application_status', 'N/A')}"
    )

# ------------------------------------------------------------------
# DEBUG OPCIONAL
# ------------------------------------------------------------------
# pprint(applications)
