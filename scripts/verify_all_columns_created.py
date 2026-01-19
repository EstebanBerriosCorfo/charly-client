# scripts/verify_all_columns_created.py
# Verificar que se creen columnas para TODOS los field_names únicos

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

json_file = Path("downloads/applications_program_2429_full.json")
excel_file = Path("downloads/applications_program_2429_normalized.xlsx")

# Cargar datos
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

applications = [a for a in data['applications'] if a.get('form_answers')]

# Recolectar TODOS los field_names únicos
all_field_names = set()
for app in applications:
    for form_answer in app.get('form_answers', []):
        for field_answer in form_answer.get('field_answers', []):
            field = field_answer.get('field', {})
            field_name = field.get('name', '')
            if field_name:
                all_field_names.add(field_name)

print(f"Total field_names únicos en JSON: {len(all_field_names)}")

# Cargar Excel
df = pd.read_excel(excel_file)
excel_columns = set(df.columns)

# Excluir columnas de metadata
metadata_cols = {
    'application_id', 'application_name', 'program_id', 'provider_id',
    'application_status', 'company_application_status',
    'company_id', 'company_name', 'name', 'email', 'company_email', 'company_phone',
    'applied_at', 'application_sent_at', 'last_form_submit', 'created_at', 'updated_at',
    'complete_forms', 'form_answers_count', 'assigned_evaluators_count',
    'application_sent', 'score_algo', 'score_eval', 'score_admin', 'score_total', 'comment'
}

excel_response_cols = excel_columns - metadata_cols

print(f"Columnas en Excel (total): {len(df.columns)}")
print(f"Columnas de metadata: {len(metadata_cols & excel_columns)}")
print(f"Columnas de respuestas en Excel: {len(excel_response_cols)}")

# Verificar si hay field_names que no tienen columna correspondiente
# Esto es difícil porque los nombres de columna son descriptivos, no field_names
# Pero podemos verificar que el número de columnas sea razonable

print(f"\nDiferencia: {len(all_field_names)} field_names únicos vs {len(excel_response_cols)} columnas de respuestas")
print(f"Si cada field_name = 1 columna base, esperaríamos al menos {len(all_field_names)} columnas")
print(f"Con expansión de repeticiones, podríamos tener más")

# Contar cuántas veces aparece cada field_name en las aplicaciones
field_name_counts = defaultdict(int)
for app in applications:
    app_fields = set()
    for form_answer in app.get('form_answers', []):
        for field_answer in form_answer.get('field_answers', []):
            field = field_answer.get('field', {})
            field_name = field.get('name', '')
            if field_name:
                app_fields.add(field_name)
                field_name_counts[field_name] += 1

# Calcular columnas necesarias considerando repeticiones
total_cols_needed = 0
for field_name, total_count in field_name_counts.items():
    # Cada field_name aparece en múltiples aplicaciones
    # Pero en cada aplicación, puede aparecer múltiples veces
    # Necesitamos contar el máximo de repeticiones en una sola aplicación
    max_in_single_app = 0
    for app in applications:
        count_in_app = 0
        for form_answer in app.get('form_answers', []):
            for field_answer in form_answer.get('field_answers', []):
                if field_answer.get('field', {}).get('name', '') == field_name:
                    count_in_app += 1
        if count_in_app > max_in_single_app:
            max_in_single_app = count_in_app
    
    # Columnas necesarias: 1 base + (max_repeats - 1) expandidas
    if max_in_single_app > 0:
        total_cols_needed += max_in_single_app
    else:
        total_cols_needed += 1

print(f"\nEstimación de columnas necesarias (con expansión): {total_cols_needed}")
print(f"Columnas actuales: {len(df.columns)}")
print(f"Faltantes: {total_cols_needed - len(df.columns)}")
