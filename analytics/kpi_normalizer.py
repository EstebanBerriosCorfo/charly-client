# analytics/kpi_normalizer.py
# ================================================================
# Normalizador de KPIs (Fields)
# Objetivo: transformar KPI chart-like en tablas planas BI-ready
# ================================================================

from __future__ import annotations

from typing import Dict, Any, List


class KPINormalizer:
    """
    Normaliza KPIs (fields) y su data agregada en estructuras tabulares.

    Salidas principales:
    - kpi_metadata_table
    - kpi_data_table

    Diseño:
    - Separación estricta metadata vs data
    - Llaves listas para JOIN y BI
    """

    # ------------------------------------------------------------------
    # NIVEL 1 — METADATA KPI
    # ------------------------------------------------------------------
    @staticmethod
    def normalize_kpi_metadata(kpi: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normaliza la metadata de un KPI (field).
        """
        return {
            "field_id": kpi.get("id"),
            "organization_id": kpi.get("organization_id"),
            "field_type": kpi.get("field_type"),
            "component_type": kpi.get("component_type"),
            "field_function": kpi.get("field_function"),
            "weight": kpi.get("weight"),
            "question": kpi.get("question"),
            "description": kpi.get("description"),
            "created_at": kpi.get("created_at"),
            "updated_at": kpi.get("updated_at"),
        }

    # ------------------------------------------------------------------
    # NIVEL 2 — DATA KPI (SERIES)
    # ------------------------------------------------------------------
    @staticmethod
    def normalize_kpi_data(kpi: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Normaliza la data agregada de un KPI.

        Transforma:
        labels + datasets → filas tabulares
        """
        rows: List[Dict[str, Any]] = []

        data_block = kpi.get("data")
        if not data_block:
            return rows

        labels = data_block.get("labels", [])
        datasets = data_block.get("datasets", [])

        for dataset in datasets:
            dataset_label = dataset.get("label")
            values = dataset.get("data", [])

            for idx, value in enumerate(values):
                rows.append({
                    "field_id": kpi.get("id"),
                    "organization_id": kpi.get("organization_id"),
                    "label": labels[idx] if idx < len(labels) else None,
                    "dataset_label": dataset_label,
                    "value": value,
                })

        return rows

    # ------------------------------------------------------------------
    # NORMALIZACIÓN COMPLETA
    # ------------------------------------------------------------------
    @classmethod
    def normalize_kpi_full(
        cls,
        kpi: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Normaliza un KPI completo separando metadata y data.
        """
        return {
            "kpi_metadata": [cls.normalize_kpi_metadata(kpi)],
            "kpi_data": cls.normalize_kpi_data(kpi),
        }