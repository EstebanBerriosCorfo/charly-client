# analytics/application_normalizer.py
# ================================================================
# Normalizador de postulaciones y respuestas (Applications)
# Objetivo: transformar JSON anidado en tablas planas (BI-ready)
# ================================================================

from __future__ import annotations

from typing import Dict, Any, List


class ApplicationNormalizer:
    """
    Normaliza postulaciones (applications) y sus respuestas
    a estructuras tabulares planas.

    Salidas principales:
    - applications_table
    - form_answers_table
    - field_answers_table

    NOTA:
    - No depende de pandas (para máxima portabilidad)
    - Pensado para SQL / Power BI / ETL
    """

    # ------------------------------------------------------------------
    # NIVEL 1 — POSTULACIONES
    # ------------------------------------------------------------------
    @staticmethod
    def normalize_application(application: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normaliza metadata principal de una postulación.
        """
        return {
            "application_id": application.get("id"),
            "program_id": application.get("program_id"),
            "application_name": application.get("name"),
            "application_status": application.get("application_status"),
            "company_application_status": application.get("company_application_status"),
            "application_sent_at": application.get("application_sent_at"),
            "assigned_evaluators_count": application.get("assigned_evaluators_count"),
            "form_answers_count": application.get("form_answers_count"),
            "score_admin": application.get("score_admin"),
            "score_algo": application.get("score_algo"),
            "score_eval": application.get("score_eval"),
            "company_id": application.get("company", {}).get("id"),
            "company_name": application.get("company", {}).get("name"),
            "company_email": application.get("company", {}).get("email"),
        }

    # ------------------------------------------------------------------
    # NIVEL 2 — FORM ANSWERS
    # ------------------------------------------------------------------
    @staticmethod
    def normalize_form_answers(application: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Normaliza respuestas por formulario (form_answers).
        """
        rows: List[Dict[str, Any]] = []

        for form_answer in application.get("form_answers", []):
            rows.append({
                "application_id": application.get("id"),
                "form_answer_id": form_answer.get("id"),
                "form_id": form_answer.get("form_id"),
                "form_name": form_answer.get("form", {}).get("name"),
                "form_title": form_answer.get("form", {}).get("title"),
                "answered_at": form_answer.get("answered_at"),
            })

        return rows

    # ------------------------------------------------------------------
    # NIVEL 3 — FIELD ANSWERS (KPI / preguntas)
    # ------------------------------------------------------------------
    @staticmethod
    def normalize_field_answers(application: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Normaliza respuestas por campo (field_answers).
        Cada fila = una respuesta a una pregunta.
        """
        rows: List[Dict[str, Any]] = []

        for form_answer in application.get("form_answers", []):
            form_answer_id = form_answer.get("id")

            for field_answer in form_answer.get("field_answers", []):
                field = field_answer.get("field", {})

                rows.append({
                    "application_id": application.get("id"),
                    "program_id": application.get("program_id"),
                    "company_id": application.get("company", {}).get("id"),
                    "form_answer_id": form_answer_id,
                    "field_answer_id": field_answer.get("id"),
                    "field_id": field.get("id"),
                    "field_name": field.get("name"),
                    "field_question": field.get("question"),
                    "field_type": field.get("field_type"),
                    "component_type": field.get("component_type"),
                    "answer": field_answer.get("answer"),
                    "answered_at": form_answer.get("answered_at"),
                })

        return rows

    # ------------------------------------------------------------------
    # NORMALIZACIÓN COMPLETA
    # ------------------------------------------------------------------
    @classmethod
    def normalize_application_full(
        cls,
        application: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Normaliza una postulación completa en todas sus tablas.
        """
        return {
            "applications": [cls.normalize_application(application)],
            "form_answers": cls.normalize_form_answers(application),
            "field_answers": cls.normalize_field_answers(application),
        }