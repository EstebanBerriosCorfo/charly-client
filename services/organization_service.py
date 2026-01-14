# services/organization_service.py
# ================================================================
# Organization Service
# Endpoints:
#   - GET /organizations
#   - GET /organizations/{organization_id}
# Objetivo: contrato API limpio para organizaciones
# ================================================================

from __future__ import annotations

from typing import Dict, Any, Iterable

from core.client import CharlyApiClient
from core.endpoints import get_endpoint


class OrganizationService:
    """
    Servicio de organizaciones para la API de Charly.

    Responsabilidades:
    - Listar organizaciones disponibles
    - Obtener una organización específica

    NO:
    - Aplica lógica de negocio
    - Transforma datos
    - Maneja paginación manual (usar client.paginate)
    """

    def __init__(self, client: CharlyApiClient):
        self.client = client
        self._list_spec = get_endpoint("list_organizations")
        self._get_spec = get_endpoint("get_organization")

    # ------------------------------------------------------------------
    # LISTADO (contrato API puro)
    # ------------------------------------------------------------------
    def list_organizations(self) -> Dict[str, Any]:
        """
        Retorna el payload completo de organizaciones (paginado).

        :return: dict con keys: count, previous, next, results
        """
        return self.client.request(
            method=self._list_spec.method,
            endpoint=self._list_spec.path,
        )

    def iterate_organizations(self) -> Iterable[Dict[str, Any]]:
        """
        Itera todas las organizaciones usando paginación genérica.
        """
        return self.client.paginate(
            endpoint=self._list_spec.path
        )

    # ------------------------------------------------------------------
    # LISTADO (interfaz homogénea para scripts / orquestación)
    # ------------------------------------------------------------------
    def list(self) -> list[Dict[str, Any]]:
        """
        Devuelve solo la lista de organizaciones (results).
        Conveniencia para scripts y casos de uso.
        """
        payload = self.list_organizations()
        return payload.get("results", [])

    # ------------------------------------------------------------------
    # DETALLE (contrato API puro)
    # ------------------------------------------------------------------
    def get_organization(self, organization_id: int) -> Dict[str, Any]:
        """
        Obtiene una organización específica por ID.

        :param organization_id: ID de la organización
        :return: dict con metadata de la organización
        """
        path = self._get_spec.path.format(
            organization_id=organization_id
        )

        return self.client.request(
            method=self._get_spec.method,
            endpoint=path,
        )

    # ------------------------------------------------------------------
    # DETALLE (interfaz homogénea)
    # ------------------------------------------------------------------
    def get_by_id(self, organization_id: int) -> Dict[str, Any]:
        """
        Alias semántico para get_organization.
        """
        return self.get_organization(organization_id)