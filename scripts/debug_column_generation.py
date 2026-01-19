# scripts/debug_column_generation.py
# Debug: verificar qué nombres de columna se están generando

import json
from pathlib import Path
from collections import defaultdict
import re

json_file = Path("downloads/applications_program_2429_full.json")

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

applications = [a for a in data['applications'] if a.get('form_answers')]

# Recolectar TODOS los field_names únicos
all_field_names = set()
field_metadata_global = {}

for app in applications:
    for form_answer in app.get('form_answers', []):
        form = form_answer.get('form', {})
        form_name = form.get('name', '')
        
        for field_answer in form_answer.get('field_answers', []):
            field = field_answer.get('field', {})
            field_name = field.get('name', '')
            question = field.get('question', '')
            
            if field_name:
                all_field_names.add(field_name)
                if field_name not in field_metadata_global:
                    field_metadata_global[field_name] = {
                        'question': question,
                        'form_name': form_name
                    }

print(f"Total field_names únicos: {len(all_field_names)}\n")

# Simular la generación de nombres de columna
question_to_fields = defaultdict(list)
for field_key in all_field_names:
    question = field_metadata_global.get(field_key, {}).get('question', '')
    if question:
        question_to_fields[question].append(field_key)

print("="*80)
print("CONFLICTOS DE NOMBRES DE COLUMNA")
print("="*80)

conflicts = {q: fields for q, fields in question_to_fields.items() if len(fields) > 1}
print(f"Preguntas con múltiples field_names: {len(conflicts)}\n")

for question, fields in list(conflicts.items())[:20]:
    print(f"{question[:70]}")
    print(f"  Field_names ({len(fields)}):")
    for field_name in fields[:10]:
        print(f"    - {field_name}")
    if len(fields) > 10:
        print(f"    ... y {len(fields) - 10} más")

print("\n" + "="*80)
print("SIMULACIÓN DE GENERACIÓN DE NOMBRES DE COLUMNA")
print("="*80)

column_names_generated = {}
column_name_conflicts = defaultdict(list)

for field_key in list(all_field_names)[:50]:  # Probar con primeros 50
    metadata = field_metadata_global.get(field_key, {})
    question = metadata.get('question', '')
    form_name = metadata.get('form_name', '')
    
    same_question_fields = question_to_fields.get(question, [])
    needs_differentiation = len(same_question_fields) > 1
    
    if question:
        if form_name and form_name not in question:
            column_base = f"{form_name} - {question}"
        else:
            column_base = question
        
        if needs_differentiation or field_key != question:
            numbers_found = re.findall(r'(?:row|col|sub|_)(\d+)', field_key, re.IGNORECASE)
            
            if numbers_found:
                identifier = '_'.join(numbers_found)
                column_name = f"{column_base} - {identifier}"
            else:
                all_numbers = re.findall(r'\d+', field_key)
                if all_numbers:
                    identifier = '_'.join(all_numbers[-2:]) if len(all_numbers) >= 2 else all_numbers[-1]
                    column_name = f"{column_base} - {identifier}"
                else:
                    field_parts = field_key.split('_')
                    if len(field_parts) > 1:
                        unique_part = '_'.join(field_parts[-3:]) if len(field_parts) >= 3 else '_'.join(field_parts[-2:])
                        if len(unique_part) > 50:
                            unique_part = unique_part[:50]
                        if unique_part and unique_part != question[:50]:
                            column_name = f"{column_base} - {unique_part}"
                        else:
                            column_name = field_key if needs_differentiation else column_base
                    else:
                        column_name = field_key if needs_differentiation else column_base
        else:
            column_name = column_base
    else:
        column_name = field_key
    
    column_names_generated[field_key] = column_name
    column_name_conflicts[column_name].append(field_key)

print(f"\nNombres de columna generados: {len(column_names_generated)}")
print(f"Nombres de columna únicos: {len(set(column_names_generated.values()))}")

conflicting_names = {name: fields for name, fields in column_name_conflicts.items() if len(fields) > 1}
if conflicting_names:
    print(f"\n⚠️  CONFLICTOS ENCONTRADOS: {len(conflicting_names)} nombres de columna duplicados")
    for col_name, fields in list(conflicting_names.items())[:10]:
        print(f"\n  Columna: {col_name[:70]}")
        print(f"    Field_names ({len(fields)}):")
        for field_name in fields:
            print(f"      - {field_name}")
else:
    print("\n✅ No hay conflictos en los nombres de columna generados")
