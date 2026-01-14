# ================================================================
# DataFrame Builder
# Convierte postulaciones completas en tabla plana
# ================================================================

import pandas as pd


def build_applications_dataframe(applications: list[dict]) -> pd.DataFrame:
    """
    Convierte la lista de postulaciones (include_data=true)
    en un DataFrame plano:
        - 1 fila = 1 postulación
        - columnas = metadata + preguntas
    """

    rows = []

    for app in applications:
        base = {
            "application_id": app.get("id"),
            "application_name": app.get("name"),
            "program_id": app.get("program_id"),
            "application_status": app.get("application_status"),
            "company_id": app.get("company", {}).get("id"),
            "company_name": app.get("company", {}).get("name"),
            "company_email": app.get("company", {}).get("email"),
            "application_sent_at": app.get("application_sent_at"),
            "score_algo": app.get("score_algo"),
            "score_eval": app.get("score_eval"),
            "score_admin": app.get("score_admin"),
        }

        # Respuestas a formularios
        for form in app.get("form_answers", []):
            for field in form.get("field_answers", []):
                question = field["field"]["question"]
                answer = field.get("answer")
                base[question] = answer

        rows.append(base)

    return pd.DataFrame(rows)
