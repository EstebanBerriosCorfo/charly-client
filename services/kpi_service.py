# services/kpi_service.py
# ================================================================
# KPI Service (Fields / KPIs)
# Endpoints:
#   - GET /mgr/fields
#   - GET /mgr/fields/{field_id}
# Objetivo: contrato API limpio para KPIs y métricas
# ================================================================

from __future__ import annotations

from typing import Dict, Any

from core.client import CharlyApiClient
from core.endpoints import get_endpoint


class KPIService:
    """
    Servicio de KPIs (fields) para la API de Charly.

    Responsabilidades:
    - Listar KPIs disponibles por organización
    - Obtener un KPI específico con su data agregada

    NOTA:
    - No transforma ni normaliza datos
    - La normalización vive en analytics/
    """

    def __init__(self, client: CharlyApiClient):
        self.client = client
        self._list_spec = get_endpoint("list_kpis")
        self._get_spec = get_endpoint("get_kpi")

    # ------------------------------------------------------------------
    # LISTADO
    # ------------------------------------------------------------------
    def list_kpis(self, organization_id: int) -> Dict[str, Any]:
        """
        Lista KPIs disponibles para una organización.

        :param organization_id: ID de la organización
        :return: payload paginado (count, previous, next, results)
        """
        return self.client.request(
            method=self._list_spec.method,
            endpoint=self._list_spec.path,
            params={
                "organization_id": organization_id
            }
        )

    def iterate_kpis(self, organization_id: int):
        """
        Itera todos los KPIs de una organización usando
        paginación genérica.
        """
        return self.client.paginate(
            endpoint=self._list_spec.path,
            params={
                "organization_id": organization_id
            }
        )

    # ------------------------------------------------------------------
    # DETALLE
    # ------------------------------------------------------------------
    def get_kpi(
        self,
        field_id: int,
        organization_id: int
    ) -> Dict[str, Any]:
        """
        Obtiene un KPI específico con su data agregada.

        :param field_id: ID del KPI (field)
        :param organization_id: ID de la organización
        :return: dict con metadata del KPI y bloque 'data'
        """
        path = self._get_spec.path.format(
            field_id=field_id
        )

        return self.client.request(
            method=self._get_spec.method,
            endpoint=path,
            params={
                "organization_id": organization_id
            }
        )