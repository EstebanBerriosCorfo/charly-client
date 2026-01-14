# services/user_service.py
# ================================================================
# User Service
# Endpoint: GET /current_user
# Objetivo: acceso al contexto del usuario autenticado
# ================================================================

from __future__ import annotations

from typing import Dict, Any

from core.client import CharlyApiClient
from core.endpoints import get_endpoint


class UserService:
    """
    Servicio de usuario para la API de Charly.

    Responsabilidad única:
    - Obtener información del usuario activo (/current_user)

    NO:
    - Valida permisos
    - Aplica lógica de negocio
    - Transforma datos
    """

    def __init__(self, client: CharlyApiClient):
        self.client = client
        self.endpoint_spec = get_endpoint("current_user")

    def get_current_user(self) -> Dict[str, Any]:
        """
        Retorna la información del usuario autenticado.

        :return: dict con metadata del usuario, empresas, incubadoras, etc.
        """
        return self.client.request(
            method=self.endpoint_spec.method,
            endpoint=self.endpoint_spec.path,
        )