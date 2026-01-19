# scripts/check_field_names.py
# Verificar si los field_name tienen números que indican campos separados

import json
from pathlib import Path
from collections import defaultdict
import re

json_file = Path("downloads/applications_program_2429_full.json")

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

applications = [a for a in data['applications'] if a.get('form_answers')]

print(f"Analizando {len(applications)} aplicaciones...\n")

# Recolectar TODOS los field_name únicos
all_field_names = set()
field_name_details = defaultdict(lambda: {'count': 0, 'questions': set(), 'forms': set()})

for app in applications[:200]:  # Analizar primeras 200
    for form_answer in app.get('form_answers', []):
        form = form_answer.get('form', {})
        form_name = form.get('name', '')
        
        for field_answer in form_answer.get('field_answers', []):
            field = field_answer.get('field', {})
            field_name = field.get('name', '')
            question = field.get('question', '')
            
            if field_name:
                all_field_names.add(field_name)
                field_name_details[field_name]['count'] += 1
                field_name_details[field_name]['questions'].add(question)
                field_name_details[field_name]['forms'].add(form_name)

print("="*80)
print("ANÁLISIS DE FIELD_NAMES")
print("="*80)
print(f"Total field_names únicos: {len(all_field_names)}")

# Buscar field_names con números (como "Contribuyente Mandante 1", "Contribuyente Mandante 2")
numbered_fields = defaultdict(list)

for field_name in all_field_names:
    # Buscar patrones como "campo_1", "campo-1", "campo 1", "campo_1_subcampo"
    match = re.search(r'(.+?)[\s_-](\d+)(?:[\s_-]|$)', field_name)
    if match:
        base = match.group(1)
        number = int(match.group(2))
        numbered_fields[base].append((number, field_name))

print("\n" + "="*80)
print("FIELD_NAMES CON NÚMEROS (CAMPOS SEPARADOS)")
print("="*80)

for base, items in sorted(numbered_fields.items(), key=lambda x: len(x[1]), reverse=True)[:30]:
    if len(items) > 1:
        sorted_items = sorted(items, key=lambda x: x[0])
        print(f"\n{base}:")
        print(f"  Total variantes: {len(sorted_items)}")
        for number, full_name in sorted_items[:10]:
            details = field_name_details[full_name]
            question_sample = list(details['questions'])[0][:60] if details['questions'] else 'N/A'
            print(f"  {number:2d}. {full_name[:60]:<60} ({details['count']:4d} respuestas) - {question_sample}")

print("\n" + "="*80)
print("BUSCAR ESPECÍFICAMENTE 'Contribuyente Mandante'")
print("="*80)

contribuyente_fields = [fn for fn in all_field_names if 'contribuyente' in fn.lower() and 'mandante' in fn.lower()]

if contribuyente_fields:
    print(f"Total field_names con 'Contribuyente Mandante': {len(contribuyente_fields)}\n")
    for field_name in sorted(contribuyente_fields):
        details = field_name_details[field_name]
        questions = list(details['questions'])
        print(f"{field_name}")
        print(f"  Respuestas: {details['count']}")
        print(f"  Formularios: {', '.join(details['forms'])}")
        if questions:
            print(f"  Pregunta ejemplo: {questions[0][:80]}")
        print()
else:
    print("No se encontraron field_names con 'Contribuyente Mandante'")

print("\n" + "="*80)
print("ESTIMACIÓN CORREGIDA DE COLUMNAS")
print("="*80)

# Si cada field_name único debe ser una columna separada
total_unique_fields = len(all_field_names)

# Contar campos repetidos por field_name
max_repeats_by_field = {}
for app in applications[:200]:
    field_counts = defaultdict(int)
    for form_answer in app.get('form_answers', []):
        for field_answer in form_answer.get('field_answers', []):
            field = field_answer.get('field', {})
            field_name = field.get('name', '')
            if field_name:
                field_counts[field_name] += 1
    
    for field_name, count in field_counts.items():
        if field_name not in max_repeats_by_field or max_repeats_by_field[field_name] < count:
            max_repeats_by_field[field_name] = count

# Calcular columnas necesarias usando field_name
total_cols_by_field_name = 0
for field_name, max_repeats in max_repeats_by_field.items():
    if max_repeats > 1:
        total_cols_by_field_name += max_repeats
    else:
        total_cols_by_field_name += 1

print(f"Usando field_name como clave única:")
print(f"  Field_names únicos: {len(all_field_names)}")
print(f"  Columnas estimadas (con expansión): {total_cols_by_field_name}")
print(f"\nColumnas actuales: 317")
print(f"Diferencia: {total_cols_by_field_name - 317}")
