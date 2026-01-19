# scripts/list_all_columns.py
# Listar todas las columnas del Excel generado

import pandas as pd
from pathlib import Path

excel_file = Path("downloads/applications_program_2429_normalized.xlsx")

if not excel_file.exists():
    print(f"ERROR: No se encuentra el archivo {excel_file}")
    exit(1)

print(f"Leyendo Excel: {excel_file}\n")

# Leer Excel
df = pd.read_excel(excel_file, sheet_name="Postulaciones")

print("="*100)
print("TODAS LAS COLUMNAS DEL EXCEL")
print("="*100)
print(f"Total columnas: {len(df.columns)}\n")

# Agrupar columnas por categoría
metadata_cols = [
    "application_id", "application_name", "program_id", "provider_id",
    "application_status", "company_application_status",
    "company_id", "company_name", "name", "email", "company_email", "company_phone",
    "applied_at", "application_sent_at", "last_form_submit", "created_at", "updated_at",
    "complete_forms", "form_answers_count", "assigned_evaluators_count",
    "application_sent", "score_algo", "score_eval", "score_admin", "score_total",
    "comment"
]

metadata_found = [col for col in metadata_cols if col in df.columns]
response_cols = [col for col in df.columns if col not in metadata_cols]

print("="*100)
print("COLUMNAS DE METADATA")
print("="*100)
for i, col in enumerate(metadata_found, 1):
    non_null = df[col].notna().sum()
    print(f"{i:3d}. {col:<70} ({non_null:4d} valores)")

print(f"\nTotal columnas de metadata: {len(metadata_found)}")

print("\n" + "="*100)
print("COLUMNAS DE RESPUESTAS DE FORMULARIOS")
print("="*100)
print(f"Total columnas de respuestas: {len(response_cols)}\n")

# Agrupar por formulario (si tienen prefijo de formulario)
import re
form_groups = {}
other_cols = []

for col in response_cols:
    # Buscar patrón "Formulario - Pregunta"
    match = re.match(r'^(.+?)\s*-\s*(.+)$', col)
    if match:
        form_name = match.group(1)
        question = match.group(2)
        if form_name not in form_groups:
            form_groups[form_name] = []
        form_groups[form_name].append((question, col))
    else:
        other_cols.append(col)

# Mostrar agrupado por formulario
for form_name, questions in sorted(form_groups.items()):
    print(f"\n--- {form_name} ({len(questions)} campos) ---")
    for i, (question, full_col) in enumerate(questions[:30], 1):  # Mostrar primeros 30
        non_null = df[full_col].notna().sum()
        # Detectar si es columna numerada
        is_numbered = re.search(r'\s+\d+$', full_col)
        marker = " [NUM]" if is_numbered else ""
        print(f"  {i:3d}. {question[:65]:<65}{marker} ({non_null:4d} valores)")
    
    if len(questions) > 30:
        print(f"  ... y {len(questions) - 30} campos más")

if other_cols:
    print(f"\n--- Otras columnas ({len(other_cols)}) ---")
    for i, col in enumerate(other_cols[:20], 1):
        non_null = df[col].notna().sum()
        print(f"  {i:3d}. {col[:80]:<80} ({non_null:4d} valores)")
    if len(other_cols) > 20:
        print(f"  ... y {len(other_cols) - 20} columnas más")

print("\n" + "="*100)
print("RESUMEN DE COLUMNAS NUMERADAS (CAMPOS EXPANDIDOS)")
print("="*100)

# Contar columnas numeradas por campo base
numbered_by_base = {}
for col in df.columns:
    match = re.search(r'^(.+?)\s+(\d+)$', col)
    if match:
        base = match.group(1)
        number = int(match.group(2))
        if base not in numbered_by_base:
            numbered_by_base[base] = []
        numbered_by_base[base].append((number, col))

# Mostrar campos expandidos
for base, items in sorted(numbered_by_base.items(), key=lambda x: len(x[1]), reverse=True)[:20]:
    max_num = max(num for num, _ in items)
    non_null_total = sum(df[col].notna().sum() for _, col in items)
    print(f"\n{base[:70]}")
    print(f"  Columnas: {len(items) + 1} (base + {len(items)} expandidas, hasta {max_num})")
    print(f"  Total valores no nulos: {non_null_total}")

print("\n" + "="*100)
print("EXPORTAR LISTA COMPLETA A ARCHIVO")
print("="*100)

output_file = Path("downloads/columnas_completas.txt")
with open(output_file, "w", encoding="utf-8") as f:
    f.write("="*100 + "\n")
    f.write("LISTA COMPLETA DE COLUMNAS\n")
    f.write("="*100 + "\n")
    f.write(f"Total columnas: {len(df.columns)}\n\n")
    
    f.write("COLUMNAS DE METADATA:\n")
    f.write("-"*100 + "\n")
    for i, col in enumerate(metadata_found, 1):
        non_null = df[col].notna().sum()
        f.write(f"{i:3d}. {col:<70} ({non_null:4d} valores)\n")
    
    f.write(f"\n\nCOLUMNAS DE RESPUESTAS ({len(response_cols)}):\n")
    f.write("-"*100 + "\n")
    for i, col in enumerate(response_cols, 1):
        non_null = df[col].notna().sum()
        is_numbered = " [NUM]" if re.search(r'\s+\d+$', col) else ""
        f.write(f"{i:4d}. {col:<85}{is_numbered} ({non_null:4d} valores)\n")

print(f"Lista completa guardada en: {output_file}")
