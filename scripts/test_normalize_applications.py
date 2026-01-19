# scripts/test_normalize_applications.py
# ================================================================
# Script de prueba para normalizar aplicaciones desde JSON existente
# ================================================================

import sys
import json
from pathlib import Path

# ------------------------------------------------------------------
# Ajuste de path del proyecto
# ------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ------------------------------------------------------------------
# Imports del sistema
# ------------------------------------------------------------------
from utils.dataframe_builder import build_applications_dataframe
from utils.excel_exporter import export_applications_dataframe_to_excel

# ------------------------------------------------------------------
# CARGAR DATOS DESDE JSON
# ------------------------------------------------------------------
json_file = Path("downloads/applications_program_2429_full.json")

if not json_file.exists():
    print(f"ERROR: No se encuentra el archivo {json_file}")
    print("   Ejecuta primero el script 05_02_applications_by_program_full.py")
    sys.exit(1)

print(f"> Cargando datos desde {json_file}...")

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

applications = data.get("applications", [])
program_id = data.get("program_id")
program_name = data.get("program_name")

print(f"OK Datos cargados:")
print(f"   Program ID: {program_id}")
print(f"   Program Name: {program_name}")
print(f"   Total aplicaciones: {len(applications)}")

if not applications:
    print("ERROR: No hay aplicaciones en el archivo JSON")
    sys.exit(1)

# ------------------------------------------------------------------
# NORMALIZAR DATOS
# ------------------------------------------------------------------
print("\n> Normalizando datos a tabla plana...")

try:
    df = build_applications_dataframe(applications)
    print(f"OK Tabla creada exitosamente:")
    print(f"   Filas: {len(df)}")
    print(f"   Columnas: {len(df.columns)}")
    
    # Mostrar primeras columnas
    print(f"\nPrimeras 20 columnas:")
    for i, col in enumerate(df.columns[:20], 1):
        non_null_count = df[col].notna().sum()
        print(f"   {i:2d}. {col[:60]:<60} ({non_null_count} valores)")
    
    if len(df.columns) > 20:
        print(f"   ... y {len(df.columns) - 20} columnas mas")
    
    # Mostrar estadísticas
    print(f"\nEstadisticas:")
    print(f"   Columnas con datos: {df.notna().any(axis=0).sum()}")
    print(f"   Columnas vacias: {(df.isna().all(axis=0)).sum()}")
    
    # Mostrar algunas filas de ejemplo
    print(f"\nPrimeras 3 filas (primeras 10 columnas):")
    print(df.iloc[:3, :10].to_string())
    
except Exception as e:
    print(f"ERROR al normalizar: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ------------------------------------------------------------------
# EXPORTAR A EXCEL
# ------------------------------------------------------------------
print("\n> Exportando a Excel...")

output_file = f"applications_program_{program_id}_normalized.xlsx"
output_path = Path("downloads") / output_file

try:
    export_applications_dataframe_to_excel(df, output_path, sheet_name="Postulaciones")
    
    print(f"\nOK Excel exportado exitosamente:")
    print(f"   Archivo: {output_path}")
    print(f"   Tamano: {output_path.stat().st_size / 1024:.2f} KB")
    print(f"   Filas: {len(df)}")
    print(f"   Columnas: {len(df.columns)}")
    
except Exception as e:
    print(f"ERROR al exportar a Excel: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nOK Prueba completada exitosamente!")
