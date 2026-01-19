# scripts/test_column_names_for_contribuyente.py
# Probar la generación de nombres de columna para campos Contribuyente Mandante

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

# Simular la generación de nombres de columna
question_to_fields = defaultdict(list)
for field_key in all_field_names:
    question = field_metadata_global.get(field_key, {}).get('question', '')
    if question:
        question_to_fields[question].append(field_key)

field_to_column_name = {}

# Generar nombres de columna usando la misma lógica del código
for field_key in all_field_names:
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
                            column_name = field_key
                    else:
                        column_name = field_key if needs_differentiation else column_base
        else:
            column_name = column_base
    else:
        column_name = field_key
    
    field_to_column_name[field_key] = column_name

# Verificar duplicados
column_name_counts = defaultdict(list)
for field_key, col_name in field_to_column_name.items():
    column_name_counts[col_name].append(field_key)

print("="*80)
print("VERIFICACIÓN DE NOMBRES DE COLUMNA PARA 'Contribuyente Mandante'")
print("="*80)

contribuyente_fields = [fk for fk in all_field_names if 'contribuyente' in field_metadata_global.get(fk, {}).get('question', '').lower() and 'mandante' in field_metadata_global.get(fk, {}).get('question', '').lower()]

if contribuyente_fields:
    print(f"Total field_names con 'Contribuyente Mandante': {len(contribuyente_fields)}\n")
    for field_name in sorted(contribuyente_fields):
        col_name = field_to_column_name.get(field_name, 'N/A')
        question = field_metadata_global.get(field_name, {}).get('question', 'N/A')
        print(f"{field_name}")
        print(f"  Columna: {col_name}")
        print(f"  Pregunta: {question[:70]}")
        print()

# Verificar duplicados
duplicates = {name: fields for name, fields in column_name_counts.items() if len(fields) > 1}

print("="*80)
print("NOMBRES DE COLUMNA DUPLICADOS")
print("="*80)
if duplicates:
    print(f"Total nombres duplicados: {len(duplicates)}\n")
    for col_name, fields in list(duplicates.items())[:10]:
        print(f"{col_name[:70]}")
        print(f"  Field_names ({len(fields)}):")
        for field_name in fields[:5]:
            print(f"    - {field_name}")
        if len(fields) > 5:
            print(f"    ... y {len(fields) - 5} más")
        print()
else:
    print("No hay nombres de columna duplicados")

print(f"\nTotal field_names: {len(all_field_names)}")
print(f"Total nombres de columna únicos: {len(set(field_to_column_name.values()))}")
