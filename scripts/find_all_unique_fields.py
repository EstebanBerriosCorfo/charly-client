# scripts/find_all_unique_fields.py
# Encontrar TODOS los field_names únicos y verificar cuántos deberían ser columnas

import json
from pathlib import Path
from collections import defaultdict
import re

json_file = Path("downloads/applications_program_2429_full.json")

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

applications = [a for a in data['applications'] if a.get('form_answers')]

print(f"Analizando {len(applications)} aplicaciones...\n")

# Recolectar TODOS los field_names únicos
all_field_names = set()
field_name_to_question = {}
field_name_to_form = {}
field_name_max_repeats = defaultdict(int)

for app in applications:
    app_field_counts = defaultdict(int)
    
    for form_answer in app.get('form_answers', []):
        form = form_answer.get('form', {})
        form_name = form.get('name', '')
        
        for field_answer in form_answer.get('field_answers', []):
            field = field_answer.get('field', {})
            field_name = field.get('name', '')
            question = field.get('question', '')
            
            if field_name:
                all_field_names.add(field_name)
                field_name_to_question[field_name] = question
                field_name_to_form[field_name] = form_name
                app_field_counts[field_name] += 1
    
    # Actualizar max_repeats
    for field_name, count in app_field_counts.items():
        if field_name_max_repeats[field_name] < count:
            field_name_max_repeats[field_name] = count

print("="*80)
print("ANÁLISIS COMPLETO")
print("="*80)
print(f"Total field_names únicos: {len(all_field_names)}")

# Calcular columnas necesarias
total_base = len(all_field_names)
total_expanded = sum(max(0, max_repeats - 1) for max_repeats in field_name_max_repeats.values())
total_needed = total_base + total_expanded

print(f"Columnas base: {total_base}")
print(f"Columnas expandidas: {total_expanded}")
print(f"TOTAL COLUMNAS NECESARIAS: {total_needed}")

print("\n" + "="*80)
print("BUSCAR FIELD_NAMES CON 'Contribuyente Mandante'")
print("="*80)

contribuyente_fields = [f for f in all_field_names if 'contribuyente' in f.lower() and 'mandante' in f.lower()]

if contribuyente_fields:
    print(f"Total: {len(contribuyente_fields)}\n")
    for field_name in sorted(contribuyente_fields):
        question = field_name_to_question.get(field_name, 'N/A')
        form_name = field_name_to_form.get(field_name, 'N/A')
        max_repeats = field_name_max_repeats.get(field_name, 0)
        print(f"{field_name}")
        print(f"  Pregunta: {question[:70]}")
        print(f"  Formulario: {form_name}")
        print(f"  Max repeticiones: {max_repeats}")
        print()
else:
    print("No se encontraron field_names con 'Contribuyente Mandante'")

print("\n" + "="*80)
print("FIELD_NAMES CON PATRONES NUMERADOS")
print("="*80)

# Buscar field_names que parecen ser parte de una serie
numbered_groups = defaultdict(list)

for field_name in all_field_names:
    # Buscar patrones como "sub1", "row5", "colX", números al final
    match = re.search(r'(.+?)(?:sub|row|col|_)(\d+)', field_name, re.IGNORECASE)
    if match:
        base = match.group(1)
        number = int(match.group(2))
        numbered_groups[base].append((number, field_name))

for base, items in sorted(numbered_groups.items(), key=lambda x: len(x[1]), reverse=True)[:15]:
    if len(items) > 1:
        sorted_items = sorted(items, key=lambda x: x[0])
        print(f"\n{base[:60]}:")
        print(f"  Total variantes: {len(sorted_items)}")
        for number, full_name in sorted_items[:10]:
            question = field_name_to_question.get(full_name, 'N/A')[:50]
            print(f"    {number:2d}. {full_name[:60]:<60} - {question}")

print("\n" + "="*80)
print("ESTIMACIÓN FINAL")
print("="*80)
print(f"Si cada field_name único es una columna: {len(all_field_names)}")
print(f"Con expansión de repeticiones: {total_needed}")
print(f"\nColumnas actuales en Excel: 320")
print(f"Diferencia: {total_needed - 320}")

# Guardar lista completa
output_file = Path("downloads/all_field_names.txt")
with open(output_file, "w", encoding="utf-8") as f:
    f.write("="*80 + "\n")
    f.write("TODOS LOS FIELD_NAMES ÚNICOS\n")
    f.write("="*80 + "\n")
    f.write(f"Total: {len(all_field_names)}\n\n")
    
    for field_name in sorted(all_field_names):
        question = field_name_to_question.get(field_name, '')
        form_name = field_name_to_form.get(field_name, '')
        max_repeats = field_name_max_repeats.get(field_name, 0)
        f.write(f"{field_name}\n")
        f.write(f"  Question: {question}\n")
        f.write(f"  Form: {form_name}\n")
        f.write(f"  Max repeats: {max_repeats}\n\n")

print(f"\nLista completa guardada en: {output_file}")
