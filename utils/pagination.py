# utils/pagination.py
# ================================================================
# Iterador genérico de paginación para la API de Charly
# Objetivo: no duplicar loops, DatOps-friendly
# ================================================================

from __future__ import annotations

from typing import Any, Dict, Iterator, Optional


class PaginationIterator:
    """
    Iterador genérico para endpoints paginados de Charly.

    Requisitos del endpoint:
    - Respuesta con la forma:
      {
        "count": int,
        "previous": str | null,
        "next": str | null,
        "results": [ ... ]
      }

    Uso:
        for item in client.paginate("/programs", params={"organization_id": 1}):
            ...
    """

    def __init__(
        self,
        client,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ):
        self.client = client
        self.endpoint = endpoint
        self.params = params or {}

        self._next_url: Optional[str] = None
        self._buffer: list[Any] = []
        self._exhausted: bool = False

    def __iter__(self) -> Iterator[Any]:
        return self

    def __next__(self) -> Any:
        if not self._buffer and not self._exhausted:
            self._fetch_next_page()

        if not self._buffer:
            raise StopIteration

        return self._buffer.pop(0)

    # ------------------------------------------------------------------
    # LÓGICA INTERNA
    # ------------------------------------------------------------------
    def _fetch_next_page(self) -> None:
        """
        Obtiene la siguiente página y carga el buffer.
        """
        if self._exhausted:
            return

        if self._next_url:
            response = self.client.request(
                method="GET",
                endpoint=self._next_url,
            )
        else:
            response = self.client.request(
                method="GET",
                endpoint=self.endpoint,
                params=self.params,
            )

        if not isinstance(response, dict):
            # Respuesta inesperada → detenemos iteración
            self._exhausted = True
            return

        results = response.get("results", [])
        self._buffer.extend(results)

        next_url = response.get("next")
        if next_url:
            # next viene como URL completa → extraemos path + query
            self._next_url = self._normalize_next_endpoint(next_url)
        else:
            self._exhausted = True

    def _normalize_next_endpoint(self, next_url: str) -> str:
        """
        Normaliza la URL 'next' devuelta por la API para reutilizarla
        con el client.request().
        """
        # Ejemplo:
        # https://app.charly.io/api/v1/programs?page=2
        base = self.client.base_url
        if next_url.startswith(base):
            return next_url[len(base):]
        return next_url