# scripts/calculate_expected_columns.py
# Calcular cuántas columnas deberíamos tener considerando todas las repeticiones

import json
from pathlib import Path
from collections import defaultdict

json_file = Path("downloads/applications_program_2429_full.json")

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

applications = [a for a in data['applications'] if a.get('form_answers')]

print(f"Analizando {len(applications)} aplicaciones...\n")

# Recolectar TODOS los field_names únicos y contar repeticiones por aplicación
all_field_names = set()
field_max_repeats = defaultdict(int)

for app in applications:
    app_field_counts = defaultdict(int)
    
    for form_answer in app.get('form_answers', []):
        for field_answer in form_answer.get('field_answers', []):
            field = field_answer.get('field', {})
            field_name = field.get('name', '')
            
            if field_name:
                all_field_names.add(field_name)
                app_field_counts[field_name] += 1
    
    # Actualizar max_repeats para cada field_name
    for field_name, count in app_field_counts.items():
        if field_max_repeats[field_name] < count:
            field_max_repeats[field_name] = count

print("="*80)
print("CÁLCULO DE COLUMNAS ESPERADAS")
print("="*80)
print(f"Total field_names únicos: {len(all_field_names)}")

# Calcular columnas necesarias
# Cada field_name necesita: 1 columna base + (max_repeats - 1) columnas expandidas
total_base = len(all_field_names)
total_expanded = sum(max(0, max_repeats - 1) for max_repeats in field_max_repeats.values())
total_needed = total_base + total_expanded

print(f"Columnas base (una por field_name): {total_base}")
print(f"Columnas expandidas (para repeticiones): {total_expanded}")
print(f"TOTAL COLUMNAS NECESARIAS: {total_needed}")

print("\n" + "="*80)
print("FIELD_NAMES CON MÁS REPETICIONES")
print("="*80)
sorted_by_repeats = sorted(
    field_max_repeats.items(),
    key=lambda x: x[1],
    reverse=True
)

for field_name, max_repeats in sorted_by_repeats[:30]:
    if max_repeats > 1:
        cols_needed = max_repeats
        print(f"{field_name[:70]:<70} → {max_repeats} repeticiones → {cols_needed} columnas")

print(f"\nColumnas actuales en Excel: 320")
print(f"Columnas esperadas: {total_needed}")
print(f"Diferencia: {total_needed - 320}")
