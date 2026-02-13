# utils/logger.py
# ================================================================
# Logger estructurado para cliente Charly
# Objetivo: observabilidad, auditoría y trazabilidad
# ================================================================

from __future__ import annotations

import json
import logging
from datetime import datetime, UTC
from typing import Any, Dict, Optional


class StructuredLogger:
    """
    Logger estructurado (JSON-like) para el cliente Charly.

    Características:
    - Logging consistente y audit-ready
    - Contexto de negocio (endpoint, organization_id, program_id, etc.)
    - Compatible con archivos, stdout, ELK, Cloud Logging

    NOTA:
    - No decide handlers globales (eso se configura fuera)
    """

    def __init__(self, name: str = "charly"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(message)s"))
            self.logger.addHandler(handler)

    # ------------------------------------------------------------------
    # MÉTODOS PÚBLICOS
    # ------------------------------------------------------------------
    def info(
        self,
        message: str,
        *,
        endpoint: Optional[str] = None,
        organization_id: Optional[int] = None,
        program_id: Optional[int] = None,
        company_id: Optional[int] = None,
        application_id: Optional[int] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._log(
            level="INFO",
            message=message,
            endpoint=endpoint,
            organization_id=organization_id,
            program_id=program_id,
            company_id=company_id,
            application_id=application_id,
            extra=extra,
        )

    def warning(
        self,
        message: str,
        *,
        endpoint: Optional[str] = None,
        organization_id: Optional[int] = None,
        program_id: Optional[int] = None,
        company_id: Optional[int] = None,
        application_id: Optional[int] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._log(
            level="WARNING",
            message=message,
            endpoint=endpoint,
            organization_id=organization_id,
            program_id=program_id,
            company_id=company_id,
            application_id=application_id,
            extra=extra,
        )

    def error(
        self,
        message: str,
        *,
        endpoint: Optional[str] = None,
        organization_id: Optional[int] = None,
        program_id: Optional[int] = None,
        company_id: Optional[int] = None,
        application_id: Optional[int] = None,
        exception: Optional[Exception] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        payload = extra or {}
        if exception:
            payload["exception_type"] = exception.__class__.__name__
            payload["exception_message"] = str(exception)

            if hasattr(exception, "to_dict"):
                payload["exception_detail"] = exception.to_dict()

        self._log(
            level="ERROR",
            message=message,
            endpoint=endpoint,
            organization_id=organization_id,
            program_id=program_id,
            company_id=company_id,
            application_id=application_id,
            extra=payload,
        )

    # ------------------------------------------------------------------
    # CORE LOGGER
    # ------------------------------------------------------------------
    def _log(
        self,
        *,
        level: str,
        message: str,
        endpoint: Optional[str],
        organization_id: Optional[int],
        program_id: Optional[int],
        company_id: Optional[int],
        application_id: Optional[int],
        extra: Optional[Dict[str, Any]],
    ) -> None:
        log_record: Dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "level": level,
            "message": message,
        }

        # Contexto de negocio / técnico
        if endpoint:
            log_record["endpoint"] = endpoint
        if organization_id:
            log_record["organization_id"] = organization_id
        if program_id:
            log_record["program_id"] = program_id
        if company_id:
            log_record["company_id"] = company_id
        if application_id:
            log_record["application_id"] = application_id

        if extra:
            log_record["extra"] = extra

        serialized = json.dumps(log_record, ensure_ascii=False)

        if level == "INFO":
            self.logger.info(serialized)
        elif level == "WARNING":
            self.logger.warning(serialized)
        else:
            self.logger.error(serialized)
