# services/application_service.py
# ================================================================
# Application Service (Postulaciones)
# Endpoints:
#   - GET /applications
#   - GET /applications/{application_id}
# Objetivo: contrato API limpio para postulaciones y respuestas
# ================================================================

from __future__ import annotations

from typing import Dict, Any, Iterable, Optional

from core.client import CharlyApiClient
from core.endpoints import get_endpoint


class ApplicationService:
    """
    Servicio de postulaciones para la API de Charly.

    Responsabilidades:
    - Listar postulaciones con filtros temporales y de IDs
    - Obtener una postulación con sus respuestas (form_answers)

    NOTA:
    - include_data=True es costoso → uso consciente
    - No transforma datos (eso vive en analytics)
    """

    def __init__(self, client: CharlyApiClient):
        self.client = client
        self._list_spec = get_endpoint("list_applications")
        self._get_spec = get_endpoint("get_application")

    # ------------------------------------------------------------------
    # LISTADO
    # ------------------------------------------------------------------
    def list_applications(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        date_type: str = "created_at",
        ids: Optional[Iterable[int]] = None,
        include_data: bool = False,
    ) -> Dict[str, Any]:
        """
        Lista postulaciones aplicando filtros.

        :param start_date: fecha mínima (ISO8601, YYYY-MM-DD)
        :param end_date: fecha máxima (ISO8601, YYYY-MM-DD)
        :param date_type: created_at | updated_at
        :param ids: iterable de application_id a filtrar
        :param include_data: si True incluye respuestas y evaluaciones
        :return: payload paginado (count, previous, next, results)
        """
        params: Dict[str, Any] = {
            "date_type": date_type
        }

        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if ids:
            params["ids"] = ",".join(str(i) for i in ids)
        if include_data:
            params["include_data"] = "true"

        return self.client.request(
            method=self._list_spec.method,
            endpoint=self._list_spec.path,
            params=params,
        )

    def iterate_applications(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        date_type: str = "created_at",
        ids: Optional[Iterable[int]] = None,
        include_data: bool = False,
    ):
        """
        Itera postulaciones usando paginación genérica.
        """
        params: Dict[str, Any] = {
            "date_type": date_type
        }

        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if ids:
            params["ids"] = ",".join(str(i) for i in ids)
        if include_data:
            params["include_data"] = "true"

        return self.client.paginate(
            endpoint=self._list_spec.path,
            params=params,
        )

    # ------------------------------------------------------------------
    # DETALLE
    # ------------------------------------------------------------------
    def get_application(
        self, 
        application_id: int,
        include_all_fields: bool = True,
    ) -> Dict[str, Any]:
        """
        Obtiene una postulación específica con sus respuestas completas.

        :param application_id: ID de la postulación
        :param include_all_fields: Si True, intenta obtener todos los campos posibles
                                   (incluso los vacíos). Por defecto True para obtener
                                   estructura completa compatible con descargas directas.
        :return: dict con metadata, evaluaciones y form_answers completos
        """
        path = self._get_spec.path.format(
            application_id=application_id
        )

        # Parámetros para obtener todos los campos posibles
        params: Dict[str, Any] = {}
        
        # Intentar incluir todos los campos si está habilitado
        # Nota: El endpoint puede no soportar este parámetro, pero lo intentamos
        if include_all_fields:
            # Algunos endpoints pueden aceptar parámetros como:
            # - include_all_fields
            # - include_empty_fields
            # - full=true
            # Probamos con el más común
            params["include_all_fields"] = "true"
            params["full"] = "true"

        return self.client.request(
            method=self._get_spec.method,
            endpoint=path,
            params=params if params else None,
        )