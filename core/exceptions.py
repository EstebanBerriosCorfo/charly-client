# core/exceptions.py
# ================================================================
# Excepciones base del cliente Charly
# Objetivo: fallar bien (mensajes claros y auditables).
# ================================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Dict


@dataclass
class CharlyApiError(Exception):
    """
    Excepción base para errores provenientes de la API de Charly.

    Características:
    - Mensaje claro y audit-ready.
    - Incluye metadata útil para trazabilidad (endpoint, método, status, request_id).
    - Permite adjuntar el payload de error devuelto por la API cuando exista.

    Uso típico:
    - HTTP 4XX / 5XX
    - Respuesta inválida (JSON mal formado, estructura inesperada)
    """

    message: str
    status_code: Optional[int] = None
    method: Optional[str] = None
    endpoint: Optional[str] = None
    url: Optional[str] = None
    request_id: Optional[str] = None
    error_code: Optional[str] = None
    details: Optional[Any] = None
    response_text: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        super().__init__(self.__str__())

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializa el error para logging estructurado.
        """
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "status_code": self.status_code,
            "method": self.method,
            "endpoint": self.endpoint,
            "url": self.url,
            "request_id": self.request_id,
            "error_code": self.error_code,
            "details": self.details,
            "response_text": self.response_text,
            "payload": self.payload,
        }

    def __str__(self) -> str:
        parts = [f"[{self.__class__.__name__}] {self.message}"]

        if self.status_code is not None:
            parts.append(f"status={self.status_code}")

        if self.method:
            parts.append(f"method={self.method}")

        if self.endpoint:
            parts.append(f"endpoint={self.endpoint}")

        if self.request_id:
            parts.append(f"request_id={self.request_id}")

        if self.error_code:
            parts.append(f"error_code={self.error_code}")

        return " | ".join(parts)


@dataclass
class AuthError(CharlyApiError):
    """
    Errores de autenticación/autorización.

    Casos típicos:
    - Credenciales inválidas en /sessions
    - API key inválida
    - Falta de permisos (HTTP 401/403 en algunos escenarios)
    """
    pass


@dataclass
class RateLimitError(CharlyApiError):
    """
    Errores asociados a rate limiting / throttling.

    Casos típicos:
    - HTTP 429
    - Exceso de requests detectado por el cliente

    Campos extra:
    - retry_after_seconds: cuánto esperar antes de reintentar
    """

    retry_after_seconds: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["retry_after_seconds"] = self.retry_after_seconds
        return data

    def __str__(self) -> str:
        base = super().__str__()
        if self.retry_after_seconds is not None:
            return f"{base} | retry_after_seconds={self.retry_after_seconds}"
        return base