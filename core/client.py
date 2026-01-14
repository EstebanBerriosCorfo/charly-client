# core/client.py
# ================================================================
# Cliente HTTP base para la API de Charly
# Objetivo: Single Source of Truth
# ================================================================

from __future__ import annotations

import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Any, Dict, Optional

from core.exceptions import (
    CharlyApiError,
    AuthError,
    RateLimitError,
)
from utils.rate_limit import RateLimitHandler
from utils.pagination import PaginationIterator


class CharlyApiClient:
    """
    Cliente HTTP único para interactuar con la API de Charly.

    Responsabilidades:
    - Construcción de requests
    - Inyección automática de api_key
    - Manejo centralizado de errores
    - Integración con rate limiting
    - Punto único de acceso a la API
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: int = 120,
        rate_limit_handler: Optional[RateLimitHandler] = None,
    ):
        if not api_key:
            raise AuthError(message="API key no proporcionada al inicializar el cliente")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.rate_limit_handler = rate_limit_handler or RateLimitHandler()

    # ------------------------------------------------------------------
    # MÉTODO PRINCIPAL
    # ------------------------------------------------------------------
    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Ejecuta un request HTTP contra la API de Charly.

        :param method: GET, POST, PUT, DELETE
        :param endpoint: endpoint relativo (ej: /programs)
        :param params: query params
        :param json_body: body JSON (para POST/PUT/DELETE)
        :return: JSON decodificado
        """

        method = method.upper()
        params = params or {}
        json_body = json_body or {}

        # --------------------------------------------------------------
        # Inyección de API KEY según contrato Charly
        # --------------------------------------------------------------
        if endpoint != "/sessions":
            if method == "GET":
                params["api_key"] = self.api_key
            else:
                json_body["api_key"] = self.api_key

        url = self._build_url(endpoint, params)
        data = self._build_body(method, json_body)

        request = urllib.request.Request(
            url=url,
            data=data,
            headers={"Content-Type": "application/json"},
            method=method,
        )

        # --------------------------------------------------------------
        # Rate limit hook (pre-request)
        # --------------------------------------------------------------
        self.rate_limit_handler.before_request()

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw_body = response.read().decode("utf-8")

                # Rate limit hook (post-request)
                self.rate_limit_handler.after_response(response)

                if not raw_body:
                    return None

                try:
                    return json.loads(raw_body)
                except json.JSONDecodeError:
                    raise CharlyApiError(
                        message="Respuesta JSON inválida",
                        status_code=response.status,
                        method=method,
                        endpoint=endpoint,
                        url=url,
                        response_text=raw_body,
                    )

        except urllib.error.HTTPError as e:
            self._handle_http_error(e, method, endpoint, url)

        except urllib.error.URLError as e:
            raise CharlyApiError(
                message=f"Error de conexión con Charly: {e.reason}",
                method=method,
                endpoint=endpoint,
                url=url,
            )

        except Exception as e:
            raise CharlyApiError(
                message="Error inesperado en request a Charly",
                method=method,
                endpoint=endpoint,
                url=url,
                details=str(e),
            )

    # ------------------------------------------------------------------
    # PAGINACIÓN
    # ------------------------------------------------------------------
    def paginate(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> PaginationIterator:
        """
        Retorna un iterador de paginación para endpoints paginados.
        """
        return PaginationIterator(
            client=self,
            endpoint=endpoint,
            params=params or {},
        )

    # ------------------------------------------------------------------
    # HELPERS INTERNOS
    # ------------------------------------------------------------------
    def _build_url(self, endpoint: str, params: Dict[str, Any]) -> str:
        query = urllib.parse.urlencode(params)
        if query:
            return f"{self.base_url}{endpoint}?{query}"
        return f"{self.base_url}{endpoint}"

    def _build_body(self, method: str, json_body: Dict[str, Any]) -> Optional[bytes]:
        if method in {"POST", "PUT", "DELETE"}:
            return json.dumps(json_body).encode("utf-8")
        return None

    def _handle_http_error(
        self,
        error: urllib.error.HTTPError,
        method: str,
        endpoint: str,
        url: str,
    ) -> None:
        raw_error = error.read().decode("utf-8") if error.fp else None
        status = error.code

        # Rate limit explícito
        if status == 429:
            retry_after = error.headers.get("Retry-After")
            raise RateLimitError(
                message="Rate limit excedido al consumir API de Charly",
                status_code=status,
                method=method,
                endpoint=endpoint,
                url=url,
                retry_after_seconds=int(retry_after) if retry_after else None,
                response_text=raw_error,
            )

        # Auth / permisos
        if status in (401, 403):
            raise AuthError(
                message="Error de autenticación o permisos en API de Charly",
                status_code=status,
                method=method,
                endpoint=endpoint,
                url=url,
                response_text=raw_error,
            )

        # Errores generales API
        raise CharlyApiError(
            message="Error HTTP al consumir API de Charly",
            status_code=status,
            method=method,
            endpoint=endpoint,
            url=url,
            response_text=raw_error,
        )