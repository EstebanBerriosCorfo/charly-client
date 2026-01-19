# scripts/analyze_contribuyente_structure.py
# Analizar la estructura de campos relacionados con Contribuyente Mandante

import json
from pathlib import Path
from collections import defaultdict

json_file = Path("downloads/applications_program_2429_full.json")

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

applications = [a for a in data['applications'] if a.get('form_answers')]

print(f"Analizando {len(applications)} aplicaciones...\n")

# Buscar aplicaciones que tengan campos relacionados con Contribuyente Mandante
contribuyente_apps = []

for app in applications[:50]:  # Analizar primeras 50
    app_id = app['id']
    contribuyente_fields = []
    
    for form_answer in app.get('form_answers', []):
        form = form_answer.get('form', {})
        form_name = form.get('name', '')
        
        for field_answer in form_answer.get('field_answers', []):
            field = field_answer.get('field', {})
            field_name = field.get('name', '')
            question = field.get('question', '')
            
            if 'contribuyente' in question.lower() and 'mandante' in question.lower():
                contribuyente_fields.append({
                    'field_name': field_name,
                    'question': question,
                    'answer': field_answer.get('answer'),
                    'form_name': form_name
                })
    
    if contribuyente_fields:
        contribuyente_apps.append({
            'app_id': app_id,
            'fields': contribuyente_fields
        })

print("="*80)
print("APLICACIONES CON CAMPOS 'Contribuyente Mandante'")
print("="*80)
print(f"Total aplicaciones encontradas: {len(contribuyente_apps)}\n")

for app_info in contribuyente_apps[:5]:
    print(f"App ID: {app_info['app_id']}")
    print(f"  Total campos: {len(app_info['fields'])}")
    for field in app_info['fields']:
        print(f"    - {field['field_name']}")
        print(f"      Pregunta: {field['question'][:70]}")
        print(f"      Respuesta: {str(field['answer'])[:50]}")
    print()

# Buscar todos los field_names que tienen "sub" seguido de números
# Estos pueden representar campos repetidos
print("="*80)
print("FIELD_NAMES CON PATRÓN 'sub' (POSIBLES CAMPOS REPETIDOS)")
print("="*80)

sub_fields = defaultdict(list)

for app in applications[:100]:
    for form_answer in app.get('form_answers', []):
        for field_answer in form_answer.get('field_answers', []):
            field = field_answer.get('field', {})
            field_name = field.get('name', '')
            
            if 'sub' in field_name.lower():
                # Extraer el patrón base (antes del sub)
                import re
                match = re.match(r'(.+?)_sub(\d+)', field_name, re.IGNORECASE)
                if match:
                    base = match.group(1)
                    sub_num = match.group(2)
                    sub_fields[base].append((int(sub_num), field_name))

for base, items in sorted(sub_fields.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
    if len(items) > 1:
        sorted_items = sorted(items, key=lambda x: x[0])
        print(f"\n{base[:60]}:")
        print(f"  Total variantes: {len(sorted_items)}")
        for sub_num, full_name in sorted_items[:10]:
            print(f"    sub{sub_num}: {full_name[:70]}")
