# utils/rate_limit.py
# ================================================================
# Manejo de Rate Limit, Retry y Backoff
# Objetivo: resiliencia y control del tráfico hacia Charly
# ================================================================

from __future__ import annotations

import time
from typing import Optional

from core.exceptions import RateLimitError


class RateLimitHandler:
    """
    Handler centralizado de rate limit y retry.

    Responsabilidades:
    - Aplicar backoff antes de un request si es necesario
    - Interpretar headers de rate limit (Retry-After)
    - Dejar hook listo para alertas futuras

    NOTA:
    - No ejecuta requests
    - No conoce endpoints específicos
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_backoff_seconds: int = 2,
        max_backoff_seconds: int = 30,
    ):
        self.max_retries = max_retries
        self.base_backoff_seconds = base_backoff_seconds
        self.max_backoff_seconds = max_backoff_seconds

        self._retry_count = 0
        self._last_retry_after: Optional[int] = None

    # ------------------------------------------------------------------
    # HOOKS PÚBLICOS
    # ------------------------------------------------------------------
    def before_request(self) -> None:
        """
        Hook ejecutado antes de cada request.
        Aplica espera si hubo rate limit previo.
        """
        if self._last_retry_after:
            time.sleep(self._last_retry_after)
            self._last_retry_after = None

    def after_response(self, response) -> None:
        """
        Hook ejecutado después de cada response exitosa.
        Resetea contadores de retry.
        """
        self._retry_count = 0
        self._last_retry_after = None

    def on_rate_limit(self, error: RateLimitError) -> None:
        """
        Hook ejecutado cuando ocurre un RateLimitError.
        Decide si reintentar o propagar el error.
        """
        self._retry_count += 1

        if self._retry_count > self.max_retries:
            # Punto de extensión para alertas futuras
            self._notify_rate_limit_exceeded(error)
            raise error

        wait_seconds = self._calculate_backoff(error.retry_after_seconds)
        self._last_retry_after = wait_seconds

    # ------------------------------------------------------------------
    # MÉTODOS INTERNOS
    # ------------------------------------------------------------------
    def _calculate_backoff(self, retry_after: Optional[int]) -> int:
        """
        Calcula el tiempo de espera antes del próximo retry.
        Prioriza Retry-After si viene desde la API.
        """
        if retry_after:
            return min(retry_after, self.max_backoff_seconds)

        exponential = self.base_backoff_seconds * (2 ** (self._retry_count - 1))
        return min(exponential, self.max_backoff_seconds)

    def _notify_rate_limit_exceeded(self, error: RateLimitError) -> None:
        """
        Hook futuro para alertas (mail, Teams, Slack, etc.).
        Por ahora, es un placeholder explícito.
        """
        # TODO: integrar con sistema de alertas corporativo
        # Ejemplo futuro:
        # send_alert(
        #   level="CRITICAL",
        #   message="Rate limit excedido en API Charly",
        #   details=error.to_dict()
        # )
        pass