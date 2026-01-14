# ================================================================
# Script 05_01_01_applications_full_to_dataframe.py
#
# Objetivo:
#   Transformar el JSON completo de postulaciones (applications)
#   en un DataFrame tabular:
#
#     - 1 fila = 1 postulación
#     - Columnas fijas (metadata)
#     - Columnas dinámicas (preguntas del formulario)
#
# Fuente de datos:
#   Salida del endpoint:
#     GET /applications?program_id=XXX&include_data=true
#
# NOTA:
#   Este script NO consulta la API.
#   Opera sobre datos ya obtenidos.
# ================================================================

import pandas as pd
from typing import List, Dict, Any


# ------------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# ------------------------------------------------------------------
def build_applications_dataframe(
    applications: List[Dict[str, Any]]
) -> pd.DataFrame:
    """
    Convierte postulaciones completas en un DataFrame tabular.

    Parámetro:
        applications (list[dict]):
            Lista de postulaciones devueltas por
            /applications?include_data=true

    Retorna:
        pandas.DataFrame:
            DataFrame con:
              - 1 fila por postulación
              - columnas = metadata + preguntas
    """

    rows: List[Dict[str, Any]] = []

    for app in applications:
        row: Dict[str, Any] = {}

        # ----------------------------------------------------------
        # METADATA BASE (columnas fijas)
        # ----------------------------------------------------------
        row["application_id"] = app.get("id")
        row["application_name"] = app.get("name")
        row["program_id"] = app.get("program_id")
        row["application_status"] = app.get("application_status")
        row["application_sent_at"] = app.get("application_sent_at")

        # Scores
        row["score_algo"] = app.get("score_algo")
        row["score_eval"] = app.get("score_eval")
        row["score_admin"] = app.get("score_admin")

        # Empresa
        company = app.get("company", {})
        row["company_id"] = company.get("id")
        row["company_name"] = company.get("name")
        row["company_email"] = company.get("email")

        # ----------------------------------------------------------
        # FORMULARIOS → PREGUNTAS → RESPUESTAS
        # ----------------------------------------------------------
        form_answers = app.get("form_answers", [])

        for form_answer in form_answers:
            field_answers = form_answer.get("field_answers", [])

            for fa in field_answers:
                field = fa.get("field", {})
                question = field.get("question")
                answer = fa.get("answer")

                # Normalización: pregunta = columna
                if question:
                    row[question] = answer

        rows.append(row)

    df = pd.DataFrame(rows)

    return df

