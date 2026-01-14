# security/credential_store.py
# ================================================================
# Store local de credenciales Charly (fuera del repo)
# ================================================================

import json
from pathlib import Path
from core.exceptions import AuthError


class CredentialStore:

    def __init__(self, path: Path):
        self.path = path

        if not self.path.exists():
            raise AuthError(
                message="Archivo de credenciales Charly no encontrado",
                details={"path": str(self.path)}
            )

    def get_credentials(self, system_user: str) -> dict:
        data = json.loads(self.path.read_text(encoding="utf-8"))

        if system_user not in data:
            raise AuthError(
                message="Usuario del sistema no autorizado para Charly",
                details={"system_user": system_user}
            )

        return data[system_user]