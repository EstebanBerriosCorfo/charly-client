# scripts/find_repeated_fields.py
# Buscar campos que se repiten múltiples veces en la misma aplicación

import json
from pathlib import Path
from collections import defaultdict

json_file = Path("downloads/applications_program_2429_full.json")

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

applications = [a for a in data['applications'] if a.get('form_answers')]

print(f"Analizando {len(applications)} aplicaciones...\n")

# Buscar aplicaciones con múltiples respuestas a la misma pregunta
repeated_fields = defaultdict(list)

for app in applications[:200]:  # Analizar primeras 200
    app_id = app['id']
    question_counts = defaultdict(list)
    
    for form_answer in app.get('form_answers', []):
        for field_answer in form_answer.get('field_answers', []):
            field = field_answer.get('field', {})
            question = field.get('question', '')
            answer = field_answer.get('answer')
            
            # Solo considerar si tiene respuesta
            if answer is not None and answer != '':
                question_counts[question].append({
                    'form_answer_id': form_answer.get('id'),
                    'field_answer_id': field_answer.get('id'),
                    'answer': str(answer)[:100]
                })
    
    # Encontrar preguntas con múltiples respuestas
    for question, answers in question_counts.items():
        if len(answers) > 1:
            repeated_fields[question].append({
                'app_id': app_id,
                'count': len(answers),
                'answers': answers
            })

print("="*80)
print("CAMPOS QUE SE REPITEN MÚLTIPLES VECES EN LA MISMA APLICACIÓN")
print("="*80)

# Ordenar por frecuencia
sorted_repeated = sorted(repeated_fields.items(), key=lambda x: len(x[1]), reverse=True)

for question, apps_with_repeats in sorted_repeated[:20]:
    total_apps = len(apps_with_repeats)
    max_repeats = max(a['count'] for a in apps_with_repeats)
    
    print(f"\n{question[:80]}")
    print(f"  Aplicaciones con repeticiones: {total_apps}")
    print(f"  Máximo de repeticiones: {max_repeats}")
    
    # Mostrar ejemplo
    if apps_with_repeats:
        example = apps_with_repeats[0]
        print(f"  Ejemplo (App {example['app_id']}, {example['count']} repeticiones):")
        for i, ans in enumerate(example['answers'][:3], 1):
            print(f"    {i}. {ans['answer'][:60]}")

print("\n" + "="*80)
print("BUSCAR ESPECÍFICAMENTE 'Contribuyente Mandante'")
print("="*80)

contribuyente_fields = {k: v for k, v in repeated_fields.items() if 'Contribuyente Mandante' in k or 'contribuyente mandante' in k.lower()}

if contribuyente_fields:
    for question, apps_with_repeats in contribuyente_fields.items():
        print(f"\n{question}")
        print(f"  Aplicaciones: {len(apps_with_repeats)}")
        if apps_with_repeats:
            example = apps_with_repeats[0]
            print(f"  Ejemplo (App {example['app_id']}):")
            for i, ans in enumerate(example['answers'], 1):
                print(f"    {i}. {ans['answer'][:80]}")
else:
    print("No se encontraron campos 'Contribuyente Mandante' con repeticiones")

print("\n" + "="*80)
print("BUSCAR PATRONES DE CAMPOS NUMERADOS")
print("="*80)

# Buscar preguntas que parecen ser parte de una serie numerada
import re
numbered_questions = defaultdict(set)

for app in applications[:200]:
    for form_answer in app.get('form_answers', []):
        for field_answer in form_answer.get('field_answers', []):
            field = field_answer.get('field', {})
            question = field.get('question', '')
            
            # Buscar patrones como "Campo 1 - Subcampo", "Campo 2 - Subcampo"
            match = re.search(r'(.+?)\s+(\d+)\s*-\s*(.+)', question)
            if match:
                base = match.group(1)
                number = match.group(2)
                suffix = match.group(3)
                numbered_questions[base].add((int(number), suffix, question))

# Mostrar series numeradas
for base, items in list(numbered_questions.items())[:15]:
    if len(items) > 1:
        sorted_items = sorted(items, key=lambda x: x[0])
        print(f"\n{base}:")
        for number, suffix, full_question in sorted_items[:5]:
            print(f"  {number}: {suffix[:60]}")
