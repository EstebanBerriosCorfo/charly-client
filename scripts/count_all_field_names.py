# scripts/count_all_field_names.py
# Contar TODOS los field_names únicos en TODAS las aplicaciones

import json
from pathlib import Path
from collections import defaultdict

json_file = Path("downloads/applications_program_2429_full.json")

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

applications = [a for a in data['applications'] if a.get('form_answers')]

print(f"Analizando {len(applications)} aplicaciones...\n")

# Recolectar TODOS los field_names únicos
all_field_names = set()
field_name_info = defaultdict(lambda: {'count': 0, 'question': '', 'form_name': '', 'max_repeats': 0})

for app in applications:
    app_id = app['id']
    field_counts_per_app = defaultdict(int)
    
    for form_answer in app.get('form_answers', []):
        form = form_answer.get('form', {})
        form_name = form.get('name', '')
        
        for field_answer in form_answer.get('field_answers', []):
            field = field_answer.get('field', {})
            field_name = field.get('name', '')
            question = field.get('question', '')
            answer = field_answer.get('answer')
            
            if field_name and answer is not None and answer != "":
                all_field_names.add(field_name)
                field_name_info[field_name]['count'] += 1
                field_name_info[field_name]['question'] = question
                field_name_info[field_name]['form_name'] = form_name
                field_counts_per_app[field_name] += 1
    
    # Actualizar max_repeats
    for field_name, count in field_counts_per_app.items():
        if field_name_info[field_name]['max_repeats'] < count:
            field_name_info[field_name]['max_repeats'] = count

print("="*80)
print("ANÁLISIS COMPLETO DE FIELD_NAMES")
print("="*80)
print(f"Total field_names únicos: {len(all_field_names)}")

# Calcular columnas necesarias
total_base_columns = len(all_field_names)
total_expanded_columns = sum(
    max(0, info['max_repeats'] - 1) 
    for info in field_name_info.values()
)

total_columns_needed = total_base_columns + total_expanded_columns

print(f"\nColumnas base (una por field_name único): {total_base_columns}")
print(f"Columnas expandidas (para campos repetidos): {total_expanded_columns}")
print(f"TOTAL COLUMNAS NECESARIAS: {total_columns_needed}")

print("\n" + "="*80)
print("FIELD_NAMES CON MÁS REPETICIONES")
print("="*80)
sorted_by_repeats = sorted(
    field_name_info.items(),
    key=lambda x: x[1]['max_repeats'],
    reverse=True
)

for field_name, info in sorted_by_repeats[:20]:
    question_short = info['question'][:60] if info['question'] else 'N/A'
    print(f"\n{field_name[:70]}")
    print(f"  Total respuestas: {info['count']}")
    print(f"  Máximo repeticiones: {info['max_repeats']}")
    print(f"  Pregunta: {question_short}")
    print(f"  Formulario: {info['form_name']}")

print("\n" + "="*80)
print("EJEMPLOS DE FIELD_NAMES SIMILARES CON DIFERENTES NÚMEROS")
print("="*80)

# Buscar field_names que parecen ser parte de una serie
import re
series_groups = defaultdict(list)

for field_name in all_field_names:
    # Buscar patrones como "campo_row5", "campo_sub1", etc.
    match = re.search(r'(.+?)(?:row|sub|col)(\d+)', field_name, re.IGNORECASE)
    if match:
        base = match.group(1)
        number = match.group(2)
        series_groups[base].append((int(number), field_name))

for base, items in list(series_groups.items())[:10]:
    if len(items) > 1:
        sorted_items = sorted(items, key=lambda x: x[0])
        print(f"\n{base[:60]}:")
        print(f"  Total variantes: {len(sorted_items)}")
        for number, full_name in sorted_items[:5]:
            info = field_name_info[full_name]
            print(f"    {number}: {full_name[:70]} ({info['count']} respuestas)")
