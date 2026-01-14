# services/program_service.py
# ================================================================
# Program Service (Convocatorias)
# Endpoints:
#   - GET /programs
#   - GET /programs/{program_id}
# Objetivo: contrato API limpio para convocatorias
# ================================================================

from __future__ import annotations

from typing import Dict, Any, Optional

from core.client import CharlyApiClient
from core.endpoints import get_endpoint


class ProgramService:
    """
    Servicio de convocatorias (programs) para la API de Charly.

    Responsabilidades:
    - Listar convocatorias con filtros
    - Obtener una convocatoria con sus postulaciones

    NOTA:
    - Filtros son explícitos (evita defaults peligrosos)
    - Paginación se delega al cliente
    """

    def __init__(self, client: CharlyApiClient):
        self.client = client
        self._list_spec = get_endpoint("list_programs")
        self._get_spec = get_endpoint("get_program")

    # ------------------------------------------------------------------
    # LISTADO
    # ------------------------------------------------------------------
    def list_programs(
        self,
        organization_id: Optional[int] = None,
        application_status: Optional[str] = None,
        evaluation_status: Optional[str] = None,
        created_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Lista convocatorias aplicando filtros opcionales.

        :param organization_id: filtrar por organización
        :param application_status: draft | open | finished
        :param evaluation_status: draft | open | finished
        :param created_at: fecha mínima (YYYY-MM-DD)
        :return: payload paginado (count, previous, next, results)
        """
        params: Dict[str, Any] = {}

        if organization_id is not None:
            params["organization_id"] = organization_id
        if application_status:
            params["application_status"] = application_status
        if evaluation_status:
            params["evaluation_status"] = evaluation_status
        if created_at:
            params["created_at"] = created_at

        return self.client.request(
            method=self._list_spec.method,
            endpoint=self._list_spec.path,
            params=params,
        )

    def iterate_programs(
        self,
        organization_id: Optional[int] = None,
        application_status: Optional[str] = None,
        evaluation_status: Optional[str] = None,
        created_at: Optional[str] = None,
    ):
        """
        Itera convocatorias usando paginación genérica.
        """
        params: Dict[str, Any] = {}

        if organization_id is not None:
            params["organization_id"] = organization_id
        if application_status:
            params["application_status"] = application_status
        if evaluation_status:
            params["evaluation_status"] = evaluation_status
        if created_at:
            params["created_at"] = created_at

        return self.client.paginate(
            endpoint=self._list_spec.path,
            params=params,
        )

    # ------------------------------------------------------------------
    # DETALLE
    # ------------------------------------------------------------------
    def get_program(
        self,
        program_id: int,
        company_application_status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Obtiene una convocatoria con el listado de postulaciones.

        Endpoint:
        GET /programs/{program_id}

        :param program_id: ID de la convocatoria
        :param company_application_status:
            pending | complete | sent
        :return: dict con metadata del programa y applications
        """
        params: Dict[str, Any] = {}

        if company_application_status:
            params["company_application_status"] = company_application_status

        path = self._get_spec.path.format(
            program_id=program_id
        )

        return self.client.request(
            method=self._get_spec.method,
            endpoint=path,
            params=params,
        )

    # ------------------------------------------------------------------
    # ALIAS EXPLÍCITO (DX / scripts)
    # ------------------------------------------------------------------
    def get_program_by_id(
        self,
        program_id: int,
        company_application_status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Alias explícito de get_program().

        Se incluye para:
        - Claridad semántica en scripts
        - Alineación directa con el contrato REST (/programs/{id})
        - Evitar confusión en onboarding

        :param program_id: ID del programa
        :param company_application_status: filtro opcional de postulaciones
        """
        return self.get_program(
            program_id=program_id,
            company_application_status=company_application_status,
        )
