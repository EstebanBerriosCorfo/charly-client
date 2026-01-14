# orchestration/extract_kpis.py
# ================================================================
# Caso de uso: Extracción y normalización de KPIs
# Flujo:
#   organizations → KPIs (fields) → normalización (analytics)
#
# Objetivo:
#   - Orquestar llamadas a la API
#   - Normalizar KPIs (metadata vs data)
#   - Devolver tablas BI-ready
# ================================================================

from __future__ import annotations

from typing import Dict, Any, List, Optional

from core.client import CharlyApiClient
from services.organization_service import OrganizationService
from services.kpi_service import KPIService
from analytics.kpi_normalizer import KPINormalizer
from utils.logger import StructuredLogger


class KPIExtractor:
    """
    Orquestador para extraer KPIs por organización y
    devolver salida normalizada (BI-ready).

    NOTA:
    - La normalización se delega a analytics/KPINormalizer
    - No hay parsing manual aquí
    """

    def __init__(
        self,
        client: CharlyApiClient,
        logger: Optional[StructuredLogger] = None,
    ):
        self.client = client
        self.logger = logger or StructuredLogger("charly.extract.kpis")

        self.organization_service = OrganizationService(client)
        self.kpi_service = KPIService(client)

    # ------------------------------------------------------------------
    # EXTRACCIÓN PRINCIPAL
    # ------------------------------------------------------------------
    def extract(
        self,
        *,
        organization_ids: Optional[List[int]] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Ejecuta la extracción de KPIs por organización y
        devuelve tablas normalizadas.

        :param organization_ids: lista opcional de orgs a procesar
        :return: dict con tablas:
                 - kpi_metadata
                 - kpi_data
        """

        output: Dict[str, List[Dict[str, Any]]] = {
            "kpi_metadata": [],
            "kpi_data": [],
        }

        # --------------------------------------------------------------
        # ORGANIZATIONS
        # --------------------------------------------------------------
        organizations_iter = (
            self.organization_service.iterate_organizations()
            if not organization_ids
            else (self.organization_service.get_organization(org_id) for org_id in organization_ids)
        )

        for org in organizations_iter:
            org_id = org.get("id")
            org_name = org.get("name")

            self.logger.info(
                "Procesando KPIs de organización",
                endpoint="/mgr/fields",
                organization_id=org_id,
                extra={"organization_name": org_name},
            )

            # ----------------------------------------------------------
            # KPIs POR ORGANIZACIÓN
            # ----------------------------------------------------------
            for kpi in self.kpi_service.iterate_kpis(organization_id=org_id):
                field_id = kpi.get("id")

                self.logger.info(
                    "Procesando KPI",
                    endpoint="/mgr/fields/{field_id}",
                    organization_id=org_id,
                    extra={"field_id": field_id},
                )

                # Obtener KPI con data agregada
                kpi_full = self.kpi_service.get_kpi(
                    field_id=field_id,
                    organization_id=org_id,
                )

                normalized = KPINormalizer.normalize_kpi_full(kpi_full)

                output["kpi_metadata"].extend(normalized["kpi_metadata"])
                output["kpi_data"].extend(normalized["kpi_data"])

        return output