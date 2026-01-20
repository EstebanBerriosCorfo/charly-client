# ================================================================
# DataFrame Builder
# Convierte postulaciones completas en tabla plana
# ================================================================

import pandas as pd
from typing import Dict, Any, List
from collections import defaultdict


def build_applications_dataframe(
    applications: List[Dict[str, Any]], 
    additional_field_names: set = None
) -> pd.DataFrame:
    """
    Convierte la lista de postulaciones (include_data=true)
    en un DataFrame plano:
        - 1 fila = 1 postulación
        - columnas = metadata completa + todas las respuestas de formularios
    
    Extrae TODOS los campos disponibles de:
    - Metadata de la aplicación
    - Información de la empresa
    - Respuestas de todos los formularios (field_answers)
    
    IMPORTANTE: Crea columnas para TODOS los field_names únicos encontrados
    en TODAS las aplicaciones, incluso si una aplicación específica no tiene ese campo.
    
    Args:
        applications: Lista de aplicaciones completas con form_answers
        additional_field_names: Set opcional de field_names adicionales a incluir
                                (útil para incluir campos de otras aplicaciones)
    """

    # PASO 1: Recolectar TODOS los field_names únicos de TODAS las aplicaciones
    # Esto asegura que tengamos columnas para todos los campos posibles
    all_field_names = set(additional_field_names) if additional_field_names else set()
    field_metadata_global = {}  # Metadata global de todos los field_names
    
    for app in applications:
        for form_answer in app.get("form_answers", []):
            form = form_answer.get("form", {})
            form_name = form.get("name", "")
            
            for field_answer in form_answer.get("field_answers", []):
                field = field_answer.get("field", {})
                field_name = field.get("name", "")
                question = field.get("question", "")
                
                if field_name:
                    all_field_names.add(field_name)
                    # Guardar metadata la primera vez que vemos este field_name
                    if field_name not in field_metadata_global:
                        field_metadata_global[field_name] = {
                            'question': question,
                            'form_name': form_name
                        }
                elif question:
                    # Si no hay field_name, crear uno basado en question
                    if form_name and form_name not in question:
                        synthetic_key = f"{form_name} - {question}"
                    else:
                        synthetic_key = question
                    all_field_names.add(synthetic_key)
                    if synthetic_key not in field_metadata_global:
                        field_metadata_global[synthetic_key] = {
                            'question': question,
                            'form_name': form_name
                        }

    rows = []

    for app in applications:
        company = app.get("company", {})
        
        # Metadata básica de la aplicación
        base: Dict[str, Any] = {
            "application_id": app.get("id"),
            "application_name": app.get("name"),
            "program_id": app.get("program_id"),
            "provider_id": app.get("provider_id"),  # Si existe
            "application_status": app.get("application_status"),
            "company_application_status": app.get("company_application_status"),
            "application_sent_at": app.get("application_sent_at"),
            "applied_at": app.get("applied_at"),  # Si existe
            "created_at": app.get("created_at"),
            "updated_at": app.get("updated_at"),
        }
        
        # Información de la empresa
        base.update({
            "company_id": company.get("id"),
            "company_name": company.get("name"),
            "name": company.get("name"),  # Alias
            "email": company.get("email"),
            "company_email": company.get("email"),
            "company_phone": company.get("phone"),  # Si existe
        })
        
        # Puntajes
        base.update({
            "score_algo": app.get("score_algo"),
            "score_eval": app.get("score_eval"),
            "score_admin": app.get("score_admin"),
            "score_total": app.get("score_total"),  # Si existe
        })
        
        # Contadores y estados
        base.update({
            "complete_forms": app.get("form_answers_count", 0),
            "form_answers_count": app.get("form_answers_count", 0),
            "assigned_evaluators_count": app.get("assigned_evaluators_count", 0),
            "application_sent": app.get("application_sent_at") is not None,
        })
        
        # Comentarios y otros campos
        base.update({
            "comment": app.get("comment"),  # Si existe
        })
        
        # Obtener última fecha de envío de formulario
        last_form_submit = None
        form_answers = app.get("form_answers", [])
        if form_answers:
            # Buscar la fecha más reciente de answered_at
            answered_dates = [
                form.get("answered_at") 
                for form in form_answers 
                if form.get("answered_at")
            ]
            if answered_dates:
                last_form_submit = max(answered_dates)
        
        base["last_form_submit"] = last_form_submit
        
        # Extraer TODAS las respuestas de formularios
        # CRÍTICO: Usar field_name completo como clave única
        # Cada field_name único = una columna separada, incluso si tienen la misma question
        field_answers_dict = defaultdict(list)
        
        for form_answer in form_answers:
            form = form_answer.get("form", {})
            form_name = form.get("name", "")
            
            for field_answer in form_answer.get("field_answers", []):
                field = field_answer.get("field", {})
                question = field.get("question", "")
                field_name = field.get("name", "")
                answer = field_answer.get("answer")
                
                # Usar field_name completo como clave única
                if field_name:
                    field_key = field_name
                else:
                    # Fallback: usar question con prefijo de formulario
                    if form_name and form_name not in question:
                        field_key = f"{form_name} - {question}"
                    else:
                        field_key = question
                
                # Agregar respuesta (incluso si está vacía)
                field_answers_dict[field_key].append(answer)
        
        # Ahora procesar TODOS los field_names (incluso los que no tienen respuesta en esta app)
        # y generar nombres de columna descriptivos
        # CRÍTICO: Cada field_name único debe tener un nombre de columna único
        import re
        
        # Crear un mapeo de field_name -> nombre de columna único
        # Esto asegura que cada field_name tenga su propia columna
        field_to_column_name = {}
        
        # Primero, agrupar field_names por question para detectar conflictos
        question_to_fields = defaultdict(list)
        for field_key in all_field_names:
            metadata = field_metadata_global.get(field_key, {})
            question = metadata.get('question', '')
            if question:
                question_to_fields[question].append(field_key)
        
        # Generar nombres de columna únicos para cada field_name
        # ESTRATEGIA: Usar question como base, pero SIEMPRE agregar identificador único del field_name
        # para asegurar que cada field_name tenga su propia columna
        for field_key in all_field_names:
            metadata = field_metadata_global.get(field_key, {})
            question = metadata.get('question', '')
            form_name = metadata.get('form_name', '')
            
            # Verificar si hay otros field_names con la misma question
            same_question_fields = question_to_fields.get(question, [])
            needs_differentiation = len(same_question_fields) > 1
            
            if question:
                # Usar question como nombre base
                if form_name and form_name not in question:
                    column_base = f"{form_name} - {question}"
                else:
                    column_base = question
                
                # SIEMPRE agregar identificador único del field_name
                # Esto asegura que cada field_name tenga su propia columna
                if needs_differentiation or field_key != question:
                    # Buscar TODOS los números/identificadores en el field_name
                    # Patrones: row5, colX, sub1, números, etc.
                    numbers_found = re.findall(r'(?:row|col|sub|_)(\d+)', field_key, re.IGNORECASE)
                    
                    if numbers_found:
                        # Usar todos los números encontrados para crear identificador único
                        identifier = '_'.join(numbers_found)
                        column_name = f"{column_base} - {identifier}"
                    else:
                        # Buscar cualquier número en el field_name
                        all_numbers = re.findall(r'\d+', field_key)
                        if all_numbers:
                            # Usar los últimos números como identificador
                            identifier = '_'.join(all_numbers[-2:]) if len(all_numbers) >= 2 else all_numbers[-1]
                            column_name = f"{column_base} - {identifier}"
                        else:
                            # Si no hay números, usar parte única del field_name
                            # Extraer los últimos segmentos del field_name
                            field_parts = field_key.split('_')
                            if len(field_parts) > 1:
                                # Usar los últimos 2-3 segmentos
                                unique_part = '_'.join(field_parts[-3:]) if len(field_parts) >= 3 else '_'.join(field_parts[-2:])
                                if len(unique_part) > 50:
                                    unique_part = unique_part[:50]
                                if unique_part and unique_part != question[:50]:
                                    column_name = f"{column_base} - {unique_part}"
                                else:
                                    # Usar field_key completo como último recurso para garantizar unicidad
                                    column_name = field_key
                            else:
                                # Si no hay partes, usar field_key completo
                                column_name = field_key if needs_differentiation else column_base
                else:
                    # Sin conflictos: usar question directamente
                    column_name = column_base
            else:
                # Fallback: usar field_key directamente
                column_name = field_key
            
            field_to_column_name[field_key] = column_name
        
        # Verificar que todos los nombres de columna sean únicos
        # Si hay duplicados, usar field_name completo para garantizar unicidad
        column_name_counts = defaultdict(list)
        for field_key, col_name in field_to_column_name.items():
            column_name_counts[col_name].append(field_key)
        
        # Corregir duplicados usando field_name completo
        # Esto asegura que cada field_name único tenga su propia columna
        duplicates_found = False
        for col_name, fields in column_name_counts.items():
            if len(fields) > 1:
                duplicates_found = True
                # Hay conflictos: usar field_name completo para cada uno
                for field_key in fields:
                    # Usar field_name completo como nombre de columna para garantizar unicidad
                    field_to_column_name[field_key] = field_key
        
        # Si encontramos duplicados, informar
        if duplicates_found:
            # Esto es normal cuando múltiples field_names tienen la misma pregunta
            pass
        
        # LIMPIAR NOMBRES DE COLUMNAS: Truncar y eliminar caracteres problemáticos
        # Excel tiene límites: 255 caracteres máximo, algunos caracteres están prohibidos
        MAX_COLUMN_LENGTH = 100  # Límite conservador para Excel
        PROBLEMATIC_CHARS = ['/', '\\', '?', '*', '[', ']', ':']  # Caracteres problemáticos en Excel
        
        cleaned_column_names = {}
        for field_key, col_name in field_to_column_name.items():
            cleaned_name = col_name
            
            # Reemplazar caracteres problemáticos
            for char in PROBLEMATIC_CHARS:
                cleaned_name = cleaned_name.replace(char, '_')
            
            # Truncar si es muy largo
            if len(cleaned_name) > MAX_COLUMN_LENGTH:
                # Mantener los últimos caracteres para preservar identificadores únicos
                cleaned_name = cleaned_name[:MAX_COLUMN_LENGTH]
            
            # Asegurar que no esté vacío
            if not cleaned_name or cleaned_name.strip() == '':
                cleaned_name = field_key[:MAX_COLUMN_LENGTH] if field_key else f"field_{field_key}"
            
            cleaned_column_names[field_key] = cleaned_name
        
        # Actualizar mapeo con nombres limpios
        field_to_column_name = cleaned_column_names
        
        # VERIFICAR Y RENOMBRAR COLUMNAS DUPLICADAS CON NÚMEROS SECUENCIALES
        # Esto asegura que todas las columnas se incluyan, incluso si tienen el mismo nombre después de la limpieza
        column_name_counts = defaultdict(list)
        for field_key, col_name in field_to_column_name.items():
            column_name_counts[col_name].append(field_key)
        
        # Renombrar duplicados agregando números secuenciales
        final_column_names = {}
        for col_name, fields in column_name_counts.items():
            if len(fields) == 1:
                # Sin duplicados: usar el nombre original
                final_column_names[fields[0]] = col_name
            else:
                # Hay duplicados: renombrar con números secuenciales
                for idx, field_key in enumerate(fields, start=1):
                    if idx == 1:
                        # Primera columna mantiene el nombre original
                        final_column_names[field_key] = col_name
                    else:
                        # Columnas siguientes: agregar número
                        # Truncar si es necesario para dejar espacio para el número
                        base_name = col_name
                        max_base_length = MAX_COLUMN_LENGTH - 5  # Dejar espacio para " _N"
                        
                        if len(base_name) > max_base_length:
                            base_name = base_name[:max_base_length]
                        
                        numbered_name = f"{base_name}_{idx}"
                        final_column_names[field_key] = numbered_name
        
        # Actualizar mapeo final
        field_to_column_name = final_column_names
        
        # FUNCIÓN PARA LIMPIAR VALORES (definida antes de usarse)
        def clean_value(value):
            """Convierte valores complejos a strings para inserción segura en Excel"""
            if value is None:
                return None
            elif isinstance(value, (list, dict)):
                # Convertir listas y dicts a JSON string
                import json
                try:
                    return json.dumps(value, ensure_ascii=False)
                except:
                    return str(value)
            elif isinstance(value, (int, float, bool)):
                return value
            elif isinstance(value, str):
                # Limpiar strings muy largos (Excel tiene límite de ~32,767 caracteres por celda)
                MAX_CELL_LENGTH = 32000
                if len(value) > MAX_CELL_LENGTH:
                    return value[:MAX_CELL_LENGTH] + "... [truncado]"
                return value
            else:
                # Cualquier otro tipo: convertir a string
                return str(value)
        
        # Ahora procesar respuestas usando el mapeo
        for field_key in all_field_names:
            column_name = field_to_column_name[field_key]
            
            # Obtener respuestas para este field_key en esta aplicación
            answers = field_answers_dict.get(field_key, [])
            non_empty_answers = [a for a in answers if a is not None and a != ""]
            
            # Expandir respuestas
            if len(non_empty_answers) == 0:
                # No hay respuestas: crear columna vacía
                base[column_name] = None
            elif len(non_empty_answers) == 1:
                # Una sola respuesta: limpiar valor
                base[column_name] = clean_value(non_empty_answers[0])
            else:
                # Múltiples respuestas: crear columnas numeradas
                # Primera columna sin número
                base[column_name] = clean_value(non_empty_answers[0])
                
                # Columnas adicionales numeradas
                # IMPORTANTE: Verificar que las columnas numeradas no entren en conflicto
                # con otras columnas existentes
                existing_columns = set(base.keys())
                for idx, answer in enumerate(non_empty_answers[1:], start=2):
                    numbered_column = f"{column_name} {idx}"
                    # Limpiar nombre de columna numerada también
                    if len(numbered_column) > MAX_COLUMN_LENGTH:
                        numbered_column = numbered_column[:MAX_COLUMN_LENGTH]
                    
                    # Si la columna numerada ya existe, agregar sufijo adicional
                    original_numbered = numbered_column
                    suffix_counter = 1
                    while numbered_column in existing_columns:
                        numbered_column = f"{original_numbered}_dup{suffix_counter}"
                        suffix_counter += 1
                        # Truncar si es necesario
                        if len(numbered_column) > MAX_COLUMN_LENGTH:
                            numbered_column = numbered_column[:MAX_COLUMN_LENGTH]
                    
                    base[numbered_column] = clean_value(answer)
                    existing_columns.add(numbered_column)

        rows.append(base)

    # Crear DataFrame
    df = pd.DataFrame(rows)
    
    # Ordenar columnas: primero metadata, luego respuestas alfabéticamente
    metadata_cols = [
        "application_id", "application_name", "program_id", "provider_id",
        "application_status", "company_application_status",
        "company_id", "company_name", "name", "email", "company_email", "company_phone",
        "applied_at", "application_sent_at", "last_form_submit", "created_at", "updated_at",
        "complete_forms", "form_answers_count", "assigned_evaluators_count",
        "application_sent", "score_algo", "score_eval", "score_admin", "score_total",
        "comment"
    ]
    
    # Filtrar columnas que realmente existen
    metadata_cols = [col for col in metadata_cols if col in df.columns]
    
    # Obtener columnas de respuestas (las que no están en metadata)
    response_cols = [col for col in df.columns if col not in metadata_cols]
    response_cols.sort()  # Ordenar alfabéticamente
    
    # Reordenar DataFrame
    df = df[metadata_cols + response_cols]
    
    # VERIFICACIÓN FINAL: Renombrar columnas duplicadas en el DataFrame final
    # Esto asegura que todas las columnas se incluyan, incluso si hay duplicados
    if len(df.columns) != len(set(df.columns)):
        # Hay columnas duplicadas: renombrarlas con números secuenciales
        seen_columns = {}
        new_columns = []
        
        for col in df.columns:
            if col in seen_columns:
                # Columna duplicada: agregar número
                seen_columns[col] += 1
                counter = seen_columns[col]
                
                # Truncar nombre base si es necesario
                base_name = col
                max_base_length = MAX_COLUMN_LENGTH - 10  # Dejar espacio para " _dupN"
                
                if len(base_name) > max_base_length:
                    base_name = base_name[:max_base_length]
                
                new_col_name = f"{base_name}_dup{counter}"
                new_columns.append(new_col_name)
            else:
                # Primera ocurrencia: mantener nombre original
                seen_columns[col] = 0
                new_columns.append(col)
        
        # Renombrar columnas en el DataFrame
        df.columns = new_columns
    
    return df
