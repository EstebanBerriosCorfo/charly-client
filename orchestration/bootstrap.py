# orchestration/bootstrap.py
# ================================================================
# Bootstrap del sistema Charly
# Objetivo:
#  - Resolver usuario del sistema
#  - Obtener credenciales Charly
#  - Login (/sessions) y renovación de API key
#  - Construcción del cliente API
#  - Obtener current_user
#  - Validar entorno mínimo antes de ejecutar casos de uso
# ================================================================

from __future__ import annotations

from typing import Dict, Any
from pathlib import Path

from core.auth import CharlyAuth
from core.client import CharlyApiClient
from core.exceptions import AuthError, CharlyApiError
from services.user_service import UserService
from utils.logger import StructuredLogger

from config.config_loader import ConfigLoader

from security.user_resolver import SystemUserResolver
from security.credential_store import CredentialStore
from security.api_key_store import ApiKeyStore
from security.paths import (
    get_credential_store_path,
    get_api_key_store_path,
)


class Bootstrap:
    """
    Orquestador de bootstrap del sistema Charly.

    Responsabilidades:
    - Resolver usuario del sistema operativo
    - Autenticación contra Charly (/sessions)
    - Renovar y persistir API key por usuario
    - Construcción del cliente API
    - Obtener usuario activo
    - Validar entorno mínimo
    """

    def __init__(
        self,
        config_path: Path,
        logger: StructuredLogger | None = None,
    ):
        self.config = ConfigLoader(config_path)
        self.logger = logger or StructuredLogger("charly.bootstrap")

        # Configuración general
        env = self.config.get("charly", "environment", default="prod")
        self.base_url = self.config.get("charly", "base_url", env)
        self.timeout = self.config.get(
            "charly", "http", "timeout_seconds", default=30
        )

    # ------------------------------------------------------------------
    # BOOTSTRAP PRINCIPAL
    # ------------------------------------------------------------------
    def run(self) -> Dict[str, Any]:
        """
        Ejecuta el bootstrap completo del sistema.

        :return: dict con:
            - client
            - current_user
            - api_key
            - system_user
        """

        self.logger.info("Iniciando bootstrap del sistema Charly")

        # 1️⃣ Resolver usuario del sistema
        system_info = SystemUserResolver.resolve()
        system_user = system_info["system_user"]

        self.logger.info(
            "Usuario del sistema detectado",
            extra={
                "system_user": system_user,
                "hostname": system_info["hostname"],
            },
        )

        # 2️⃣ Cargar credenciales Charly del usuario
        credential_store = CredentialStore(get_credential_store_path())
        credentials = credential_store.get_credentials(system_user)

        # 3️⃣ Login Charly (crear sesión)
        api_key = self._login(
            username=credentials["username"],
            password=credentials["password"],
            system_user=system_user,
        )

        # 4️⃣ Persistir / actualizar API key
        api_key_store = ApiKeyStore(get_api_key_store_path())
        api_key_store.save(system_user, api_key)

        # 5️⃣ Construir cliente API
        client = self._build_client(api_key)

        # 6️⃣ Obtener usuario activo
        current_user = self._load_current_user(client)

        # 7️⃣ Validar entorno mínimo
        self._validate_environment(current_user)

        self.logger.info(
            "Bootstrap completado correctamente",
            extra={
                "system_user": system_user,
                "charly_user": current_user.get("email"),
                "companies_count": len(current_user.get("companies", [])),
            },
        )

        return {
            "system_user": system_user,
            "api_key": api_key,
            "client": client,
            "current_user": current_user,
        }

    # ------------------------------------------------------------------
    # PASOS INTERNOS
    # ------------------------------------------------------------------
    def _login(self, username: str, password: str, system_user: str) -> str:
        """
        Ejecuta login contra /sessions.
        """
        try:
            auth = CharlyAuth(
                base_url=self.base_url,
                timeout=self.timeout,
            )

            api_key = auth.create_session(username, password)

            self.logger.info(
                "Sesión Charly creada exitosamente",
                endpoint="/sessions",
                extra={
                    "system_user": system_user,
                    "charly_user": username,
                },
            )

            return api_key

        except AuthError as e:
            self.logger.error(
                "Fallo de autenticación en bootstrap",
                endpoint="/sessions",
                exception=e,
                extra={"system_user": system_user},
            )
            raise

        except Exception as e:
            self.logger.error(
                "Error inesperado durante login",
                endpoint="/sessions",
                exception=e,
                extra={"system_user": system_user},
            )
            raise

    def _build_client(self, api_key: str) -> CharlyApiClient:
        """
        Construye el cliente API.
        """
        return CharlyApiClient(
            api_key=api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )

    def _load_current_user(self, client: CharlyApiClient) -> Dict[str, Any]:
        """
        Obtiene el usuario activo (/current_user).
        """
        try:
            user_service = UserService(client)
            current_user = user_service.get_current_user()

            self.logger.info(
                "Usuario activo obtenido",
                endpoint="/current_user",
                extra={
                    "charly_user": current_user.get("email"),
                },
            )

            return current_user

        except CharlyApiError as e:
            self.logger.error(
                "Error obteniendo usuario activo",
                endpoint="/current_user",
                exception=e,
            )
            raise

    def _validate_environment(self, current_user: Dict[str, Any]) -> None:
        """
        Validaciones mínimas de entorno antes de ejecutar casos de uso.
        """
        companies = current_user.get("companies", [])

        if not companies:
            raise CharlyApiError(
                message="Usuario no tiene empresas asociadas. Entorno inválido.",
                endpoint="/current_user",
            )

        self.logger.info(
            "Validación de entorno OK",
            endpoint="/current_user",
            extra={
                "companies": [c.get("name") for c in companies],
            },
        )