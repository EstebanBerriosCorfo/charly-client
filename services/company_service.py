# services/company_service.py
# ================================================================
# Company Service
# Endpoints:
#   - GET /companies
#   - GET /companies/{company_id}
# Objetivo: contrato API limpio para empresas
# ================================================================

from __future__ import annotations

from typing import Dict, Any, Optional

from core.client import CharlyApiClient
from core.endpoints import get_endpoint


class CompanyService:
    """
    Servicio de empresas para la API de Charly.

    Responsabilidades:
    - Listar empresas por organización
    - Obtener una empresa específica dentro de una organización

    NOTA:
    - organization_id es SIEMPRE explícito (evita bugs silenciosos)
    """

    def __init__(self, client: CharlyApiClient):
        self.client = client
        self._list_spec = get_endpoint("list_companies")
        self._get_spec = get_endpoint("get_company")

    # ------------------------------------------------------------------
    # LISTADO
    # ------------------------------------------------------------------
    def list_companies(self, organization_id: int) -> Dict[str, Any]:
        """
        Retorna el payload completo de empresas para una organización
        (paginado).

        :param organization_id: ID de la organización
        :return: dict con keys: count, previous, next, results
        """
        return self.client.request(
            method=self._list_spec.method,
            endpoint=self._list_spec.path,
            params={
                "organization_id": organization_id
            }
        )

    def iterate_companies(self, organization_id: int):
        """
        Itera todas las empresas de una organización usando
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
    def get_company(
        self,
        company_id: int,
        organization_id: int
    ) -> Dict[str, Any]:
        """
        Obtiene una empresa específica dentro de una organización.

        :param company_id: ID de la empresa
        :param organization_id: ID de la organización
        :return: dict con metadata de la empresa
        """
        path = self._get_spec.path.format(
            company_id=company_id
        )

        return self.client.request(
            method=self._get_spec.method,
            endpoint=path,
            params={
                "organization_id": organization_id
            }
        )