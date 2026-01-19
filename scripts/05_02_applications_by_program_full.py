# scripts/05_02_applications_by_program_full.py
# ================================================================
# Obtener Todas las Postulaciones de una Convocatoria con Respuestas Completas
# Endpoints utilizados:
#   - GET /programs/{program_id} → Obtener lista de application_id
#   - GET /applications/{application_id} → Obtener respuestas completas de cada postulación
#
# Objetivo:
#   - Dado un program_id (ID de convocatoria)
#   - Obtener todas las postulaciones (applications) asociadas
#   - Para cada postulación, obtener respuestas completas (form_answers y field_answers)
#   - Mostrar información completa de cada postulación
#
# ⚠️ IMPORTANTE:
#   - Este script hace múltiples requests (uno por cada postulación)
#   - Puede tomar tiempo si hay muchas postulaciones
#   - Cada request obtiene TODAS las respuestas de la postulación
# ================================================================

import sys
import json
import time
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
from services.application_service import ApplicationService

# ------------------------------------------------------------------
# BOOTSTRAP
# ------------------------------------------------------------------
ctx = Bootstrap(
    config_path=Path("config/charly.yaml")
).run()

client = ctx["client"]

org_service = OrganizationService(client)
program_service = ProgramService(client)
application_service = ApplicationService(client)

# ------------------------------------------------------------------
# LISTAR ORGANIZACIONES (UX)
# ------------------------------------------------------------------
organizations = org_service.list()

print("\n=== ORGANIZACIONES DISPONIBLES ===")
for org in organizations:
    print(f"- ID: {org['id']} | Nombre: {org['name']}")

organization_id = int(input("\nIngrese el ID de la organización: ").strip())

# ------------------------------------------------------------------
# LISTAR PROGRAMAS DE LA ORGANIZACIÓN
# ------------------------------------------------------------------
programs = list(program_service.iterate_programs(organization_id=organization_id))

print("\n=== CONVOCATORIAS DISPONIBLES ===")
for program in programs:
    print(
        f"- ID: {program['id']} | "
        f"Nombre: {program['name']} | "
        f"Estado postulación: {program.get('application_status', 'N/A')} | "
        f"Estado evaluación: {program.get('evaluation_status', 'N/A')}"
    )

program_id = int(input("\nIngrese el ID de la convocatoria (program_id): ").strip())

# ------------------------------------------------------------------
# PASO 1: OBTENER LISTA DE POSTULACIONES DEL PROGRAMA
# ------------------------------------------------------------------
print(f"\n▶ Obteniendo lista de postulaciones de la convocatoria {program_id}...")

program_detail = program_service.get_program(program_id)

program_name = program_detail.get("name", "N/A")
applications_index = program_detail.get("applications", [])

print(f"✔ Convocatoria: {program_name}")
print(f"✔ Total postulaciones encontradas: {len(applications_index)}")

if not applications_index:
    print("\n⚠️  Esta convocatoria no tiene postulaciones registradas.")
    sys.exit(0)

# ------------------------------------------------------------------
# MOSTRAR RESUMEN DE POSTULACIONES
# ------------------------------------------------------------------
print("\n=== RESUMEN DE POSTULACIONES ===")
for idx, app in enumerate(applications_index, start=1):
    company = app.get("company", {})
    company_name = company.get("name", "N/A") if company else "N/A"
    
    print(
        f"{idx:03d} | "
        f"App ID: {app.get('id')} | "
        f"Empresa: {company_name[:40]} | "
        f"Estado: {app.get('application_status', 'N/A')} | "
        f"Formularios: {app.get('form_answers_count', 0)}"
    )

# ------------------------------------------------------------------
# CONFIRMACIÓN
# ------------------------------------------------------------------
print(f"\n⚠️  Se realizarán {len(applications_index)} requests para obtener respuestas completas.")
print("   Esto puede tomar varios minutos dependiendo del número de postulaciones.")
confirm = input("\n¿Continuar? [S/n]: ").strip().lower()

if confirm == "n":
    print("Operación cancelada.")
    sys.exit(0)

# ------------------------------------------------------------------
# PASO 2: OBTENER RESPUESTAS COMPLETAS DE CADA POSTULACIÓN
# ------------------------------------------------------------------
print("\n▶ Obteniendo respuestas completas de cada postulación...\n")

applications_full = []
errors = []

for idx, app_index in enumerate(applications_index, start=1):
    application_id = app_index.get("id")
    company = app_index.get("company", {})
    company_name = company.get("name", "N/A") if company else "N/A"
    
    print(f"[{idx}/{len(applications_index)}] Procesando App ID {application_id} - {company_name}...", end=" ")
    
    try:
        # Obtener postulación completa con respuestas
        application_full = application_service.get_application(application_id)
        applications_full.append(application_full)
        print("✅")
        
        # Pequeña pausa para no saturar la API
        time.sleep(0.5)
        
    except Exception as e:
        error_msg = str(e)
        errors.append({
            "application_id": application_id,
            "company": company_name,
            "error": error_msg
        })
        print(f"❌ Error: {error_msg}")

# ------------------------------------------------------------------
# OUTPUT
# ------------------------------------------------------------------
print("\n" + "="*80)
print("=== RESULTADO FINAL ===")
print("="*80)

print(f"\n✔ Postulaciones procesadas exitosamente: {len(applications_full)}")
if errors:
    print(f"⚠️  Postulaciones con errores: {len(errors)}")
    print("\nErrores:")
    for error in errors:
        print(f"  - App ID {error['application_id']} ({error['company']}): {error['error']}")

# ------------------------------------------------------------------
# MOSTRAR INFORMACIÓN DE CADA POSTULACIÓN
# ------------------------------------------------------------------
print("\n=== POSTULACIONES CON RESPUESTAS COMPLETAS ===")

for idx, application in enumerate(applications_full, start=1):
    company = application.get("company", {})
    company_name = company.get("name", "N/A") if company else "N/A"
    
    print(f"\n--- POSTULACIÓN {idx} ---")
    print(f"Application ID: {application.get('id')}")
    print(f"Nombre: {application.get('name', 'N/A')}")
    print(f"Programa ID: {application.get('program_id')}")
    print(f"Empresa: {company_name}")
    print(f"Estado: {application.get('application_status', 'N/A')}")
    print(f"Estado empresa: {application.get('company_application_status', 'N/A')}")
    
    # Puntajes
    scores = {
        "admin": application.get("score_admin"),
        "algo": application.get("score_algo"),
        "eval": application.get("score_eval")
    }
    print(f"Puntajes: {scores}")
    
    # Formularios y respuestas
    form_answers = application.get("form_answers", [])
    print(f"Total formularios respondidos: {len(form_answers)}")
    
    for form_idx, form_answer in enumerate(form_answers, start=1):
        form = form_answer.get("form", {})
        field_answers = form_answer.get("field_answers", [])
        
        print(f"\n  Formulario {form_idx}: {form.get('name', 'N/A')}")
        print(f"    Título: {form.get('title', 'N/A')}")
        print(f"    Respondido: {form_answer.get('answered_at', 'N/A')}")
        print(f"    Total campos respondidos: {len(field_answers)}")
        
        # Mostrar algunas respuestas de ejemplo
        if field_answers:
            print(f"    Primeras 3 respuestas:")
            for field_answer in field_answers[:3]:
                field = field_answer.get("field", {})
                answer = field_answer.get("answer", "N/A")
                question = field.get("question", "N/A")
                print(f"      - {question}: {answer}")

# ------------------------------------------------------------------
# NORMALIZACIÓN Y EXPORTACIÓN
# ------------------------------------------------------------------
from utils.dataframe_builder import build_applications_dataframe
from utils.excel_exporter import export_applications_dataframe_to_excel

print("\n" + "="*80)
print("=== EXPORTACIÓN DE DATOS ===")
print("="*80)

# Normalizar datos a tabla plana
print("\n▶ Normalizando datos a tabla plana...")
df = build_applications_dataframe(applications_full)

print(f"✔ Tabla creada: {len(df)} filas × {len(df.columns)} columnas")
print(f"   Columnas de metadata: {len([c for c in df.columns if c in ['application_id', 'application_name', 'program_id', 'company_id', 'company_name']])}")
print(f"   Columnas de respuestas: {len(df.columns) - 10}")

# Exportar a Excel
export_excel = input("\n¿Exportar a Excel con todos los campos? [S/n]: ").strip().lower()

if export_excel != "n":
    output_file = f"applications_program_{program_id}_full.xlsx"
    output_path = Path("downloads") / output_file
    
    # Crear directorio si no existe
    output_path.parent.mkdir(exist_ok=True)
    
    print(f"\n▶ Exportando a Excel...")
    export_applications_dataframe_to_excel(df, output_path, sheet_name="Postulaciones")
    
    print(f"\n✔ Datos exportados a: {output_path}")
    print(f"   Total postulaciones: {len(df)}")
    print(f"   Total columnas: {len(df.columns)}")
    print(f"   Tamaño del archivo: {output_path.stat().st_size / 1024:.2f} KB")
    
    # Mostrar algunas columnas como ejemplo
    print(f"\n📊 Primeras 10 columnas:")
    for col in df.columns[:10]:
        print(f"   - {col}")

# Exportar a JSON (opcional)
export_json = input("\n¿Exportar también a JSON (datos completos)? [y/N]: ").strip().lower()

if export_json == "y":
    output_file_json = f"applications_program_{program_id}_full.json"
    output_path_json = Path("downloads") / output_file_json
    
    output_data = {
        "program_id": program_id,
        "program_name": program_name,
        "total_applications": len(applications_full),
        "applications": applications_full,
        "errors": errors if errors else None
    }
    
    with open(output_path_json, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✔ JSON exportado a: {output_path_json}")
    print(f"   Tamaño del archivo: {output_path_json.stat().st_size / 1024:.2f} KB")

# ------------------------------------------------------------------
# DEBUG OPCIONAL
# ------------------------------------------------------------------
# Descomentar para ver JSON completo de la primera postulación
# if applications_full:
#     print("\n=== DEBUG (Primera postulación completa) ===")
#     print(json.dumps(applications_full[0], indent=2, ensure_ascii=False))
