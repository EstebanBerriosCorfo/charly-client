# scripts/analyze_field_structure.py
# Analizar estructura de campos para identificar campos múltiples o anidados

import json
from pathlib import Path
from collections import defaultdict

json_file = Path("downloads/applications_program_2429_full.json")

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

applications = [a for a in data['applications'] if a.get('form_answers')]

print(f"Analizando {len(applications)} aplicaciones con formularios...\n")

# Analizar estructura de respuestas
question_counts = defaultdict(int)
question_types = defaultdict(set)
multi_value_fields = []
nested_fields = []

for app in applications[:100]:  # Analizar primeras 100
    for form_answer in app.get('form_answers', []):
        for field_answer in form_answer.get('field_answers', []):
            field = field_answer.get('field', {})
            question = field.get('question', '')
            answer = field_answer.get('answer')
            
            question_counts[question] += 1
            question_types[question].add(type(answer).__name__)
            
            # Detectar arrays
            if isinstance(answer, list):
                multi_value_fields.append({
                    'question': question,
                    'app_id': app['id'],
                    'answer_type': 'list',
                    'length': len(answer),
                    'sample': str(answer)[:200]
                })
            
            # Detectar objetos/dicts
            if isinstance(answer, dict):
                nested_fields.append({
                    'question': question,
                    'app_id': app['id'],
                    'answer_type': 'dict',
                    'keys': list(answer.keys())[:10],
                    'sample': str(answer)[:200]
                })

print("="*80)
print("CAMPOS CON MÚLTIPLES VALORES (Arrays)")
print("="*80)
if multi_value_fields:
    for mf in multi_value_fields[:10]:
        print(f"\nPregunta: {mf['question'][:80]}")
        print(f"  App ID: {mf['app_id']}")
        print(f"  Tipo: {mf['answer_type']}, Longitud: {mf['length']}")
        print(f"  Muestra: {mf['sample']}")
else:
    print("No se encontraron campos con arrays")

print("\n" + "="*80)
print("CAMPOS ANIDADOS (Objetos/Dicts)")
print("="*80)
if nested_fields:
    for nf in nested_fields[:10]:
        print(f"\nPregunta: {nf['question'][:80]}")
        print(f"  App ID: {nf['app_id']}")
        print(f"  Tipo: {nf['answer_type']}")
        print(f"  Claves: {nf['keys']}")
        print(f"  Muestra: {nf['sample']}")
else:
    print("No se encontraron campos anidados")

print("\n" + "="*80)
print("PREGUNTAS MÁS FRECUENTES")
print("="*80)
sorted_questions = sorted(question_counts.items(), key=lambda x: x[1], reverse=True)
for question, count in sorted_questions[:30]:
    types = ', '.join(question_types[question])
    print(f"{count:4d} veces | {types:15s} | {question[:70]}")

print("\n" + "="*80)
print("PREGUNTAS QUE PODRÍAN SER REPETIDAS (con números)")
print("="*80)
repeated_patterns = defaultdict(list)
for question in question_counts.keys():
    # Buscar patrones como "Contribuyente Mandante 1", "Contribuyente Mandante 2", etc.
    import re
    # Extraer base del nombre si tiene número al final
    base_match = re.match(r'^(.+?)\s+(\d+)\s*-\s*(.+)$', question)
    if base_match:
        base = base_match.group(1)
        number = base_match.group(2)
        suffix = base_match.group(3)
        repeated_patterns[base].append((number, suffix, question))
    elif re.search(r'\s+\d+\s*-\s*', question):
        # Patrón como "Campo 1 - Subcampo"
        parts = re.split(r'\s+(\d+)\s*-\s*', question, 1)
        if len(parts) == 3:
            base = parts[0]
            number = parts[1]
            suffix = parts[2]
            repeated_patterns[base].append((number, suffix, question))

for base, items in list(repeated_patterns.items())[:10]:
    if len(items) > 1:
        print(f"\n{base}:")
        for number, suffix, full_question in sorted(items, key=lambda x: int(x[0])):
            print(f"  {number}: {suffix[:60]}")
