# core/auth.py
# ================================================================
# Autenticación Charly
# Endpoint: POST /sessions
# Objetivo: bootstrap seguro (obtener API KEY)
# ================================================================

import json
import urllib.parse
import urllib.request
import urllib.error
from typing import Optional

from core.exceptions import AuthError, CharlyApiError


class CharlyAuth:
    """
    Servicio de autenticación contra la API de Charly.

    Responsabilidad única:
    - Crear sesión (/sessions)
    - Retornar api_key válida

    NO:
    - Maneja otros endpoints
    - Cachea api_key
    - Aplica retries (eso vive en client / utils)
    """

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        user_agent: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        )

    def create_session(self, username: str, password: str) -> str:
        """
        Crea una sesión en Charly y retorna el api_key.

        :param username: email del usuario
        :param password: contraseña
        :return: api_key (str)
        :raises AuthError: credenciales inválidas o respuesta inesperada
        """

        url = f"{self.base_url}/sessions"

        payload = {
            "username": username,
            "password": password
        }

        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            url=url,
            data=data,
            headers=self._build_session_headers(),
            method="POST"
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw_body = response.read().decode("utf-8")

                try:
                    body = json.loads(raw_body)
                except json.JSONDecodeError:
                    raise AuthError(
                        message="Respuesta inválida al crear sesión (JSON mal formado)",
                        status_code=response.status,
                        endpoint="/sessions",
                        method="POST",
                        response_text=raw_body
                    )

                api_key: Optional[str] = body.get("api_key")

                if not api_key:
                    raise AuthError(
                        message="Respuesta válida pero api_key no presente",
                        status_code=response.status,
                        endpoint="/sessions",
                        method="POST",
                        payload=body
                    )

                return api_key

        except urllib.error.HTTPError as e:
            raw_error = e.read().decode("utf-8") if e.fp else None

            raise AuthError(
                message="Error de autenticación al crear sesión en Charly",
                status_code=e.code,
                endpoint="/sessions",
                method="POST",
                response_text=raw_error
            )

        except urllib.error.URLError as e:
            raise AuthError(
                message=f"No fue posible conectar con Charly: {e.reason}",
                endpoint="/sessions",
                method="POST"
            )

        except Exception as e:
            raise CharlyApiError(
                message="Error inesperado durante creación de sesión",
                endpoint="/sessions",
                method="POST",
                details=str(e)
            )

    def _build_session_headers(self) -> dict:
        """
        Construye headers para /sessions compatibles con protecciones WAF.
        """
        parsed = urllib.parse.urlsplit(self.base_url)
        origin = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))
        referer = f"{origin}/"

        return {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "es-CL,es;q=0.9,en;q=0.8",
            "Origin": origin,
            "Referer": referer,
            "User-Agent": self.user_agent,
        }
