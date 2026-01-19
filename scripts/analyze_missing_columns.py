# scripts/analyze_missing_columns.py
# Analizar qué campos faltan comparando con el total esperado

import json
from pathlib import Path
from collections import defaultdict

json_file = Path("downloads/applications_program_2429_full.json")

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

applications = [a for a in data['applications'] if a.get('form_answers')]

print(f"Analizando {len(applications)} aplicaciones con formularios...\n")

# Recolectar TODAS las preguntas únicas de TODAS las aplicaciones
all_questions = set()
question_by_form = defaultdict(set)
question_details = defaultdict(lambda: {'count': 0, 'forms': set(), 'max_repeats': 0})

for app in applications:
    app_id = app['id']
    question_counts_per_app = defaultdict(int)
    
    for form_answer in app.get('form_answers', []):
        form = form_answer.get('form', {})
        form_id = form.get('id')
        form_name = form.get('name', '')
        form_title = form.get('title', '')
        
        for field_answer in form_answer.get('field_answers', []):
            field = field_answer.get('field', {})
            question = field.get('question', '')
            field_name = field.get('name', '')
            answer = field_answer.get('answer')
            
            if question:
                # Crear clave única: form_name + question
                if form_name and form_name not in question:
                    full_key = f"{form_name} - {question}"
                else:
                    full_key = question
                
                all_questions.add(full_key)
                question_by_form[form_name].add(question)
                question_counts_per_app[full_key] += 1
                
                question_details[full_key]['count'] += 1
                question_details[full_key]['forms'].add(form_name)
                question_details[full_key]['max_repeats'] = max(
                    question_details[full_key]['max_repeats'],
                    question_counts_per_app[full_key]
                )

print("="*80)
print("ANÁLISIS DE CAMPOS")
print("="*80)
print(f"Total de preguntas únicas encontradas: {len(all_questions)}")
print(f"Total de formularios únicos: {len(question_by_form)}")

print("\n" + "="*80)
print("FORMULARIOS Y SUS CAMPOS")
print("="*80)
for form_name, questions in sorted(question_by_form.items()):
    print(f"\n{form_name}: {len(questions)} campos únicos")

print("\n" + "="*80)
print("CAMPOS CON MÁS REPETICIONES")
print("="*80)
sorted_by_repeats = sorted(
    question_details.items(),
    key=lambda x: x[1]['max_repeats'],
    reverse=True
)

for question_key, details in sorted_by_repeats[:30]:
    forms_list = ', '.join(list(details['forms'])[:2])
    print(f"\n{question_key[:70]}")
    print(f"  Total respuestas: {details['count']}")
    print(f"  Máximo repeticiones en una app: {details['max_repeats']}")
    print(f"  Formularios: {forms_list}")

print("\n" + "="*80)
print("ESTIMACIÓN DE COLUMNAS NECESARIAS")
print("="*80)

# Calcular columnas necesarias
total_columns_needed = 0
base_columns = len(all_questions)  # Una columna base por cada pregunta única
expanded_columns = 0

for question_key, details in question_details.items():
    if details['max_repeats'] > 1:
        # Necesitamos: 1 columna base + (max_repeats - 1) columnas expandidas
        expanded_columns += (details['max_repeats'] - 1)

total_columns_needed = base_columns + expanded_columns

print(f"Columnas base (una por pregunta única): {base_columns}")
print(f"Columnas expandidas (para campos repetidos): {expanded_columns}")
print(f"TOTAL COLUMNAS NECESARIAS: {total_columns_needed}")
print(f"\nColumnas actuales en Excel: 317")
print(f"Columnas faltantes: {total_columns_needed - 317}")

# Verificar si hay campos que se están perdiendo
print("\n" + "="*80)
print("VERIFICAR CAMPOS QUE PODRÍAN PERDERSE")
print("="*80)

# Contar campos por formulario
fields_by_form = defaultdict(lambda: defaultdict(int))

for app in applications[:100]:  # Analizar primeras 100
    for form_answer in app.get('form_answers', []):
        form = form_answer.get('form', {})
        form_name = form.get('name', '')
        
        for field_answer in form_answer.get('field_answers', []):
            field = field_answer.get('field', {})
            field_name = field.get('name', '')
            question = field.get('question', '')
            
            if field_name:
                fields_by_form[form_name][field_name] += 1

print("\nCampos únicos por formulario (por field_name):")
for form_name, fields in sorted(fields_by_form.items()):
    print(f"\n{form_name}: {len(fields)} campos únicos")
    # Mostrar algunos ejemplos
    for field_name, count in list(fields.items())[:5]:
        print(f"  - {field_name}: {count} respuestas")
