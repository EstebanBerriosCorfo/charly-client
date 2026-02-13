# security/credential_store.py
# ================================================================
# Store local de credenciales Charly (fuera del repo)
# ================================================================

import json
from pathlib import Path
from core.exceptions import AuthError
from security.secret_protector import SecretProtector


class CredentialStore:

    def __init__(self, path: Path):
        self.path = path

        if not self.path.exists():
            raise AuthError(
                message="Archivo de credenciales Charly no encontrado",
                details={"path": str(self.path)}
            )

    def get_credentials(self, system_user: str) -> dict:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise AuthError(
                message="Archivo de credenciales Charly corrupto",
                details={"path": str(self.path), "error": str(e)}
            )

        if system_user not in data:
            raise AuthError(
                message="Usuario del sistema no autorizado para Charly",
                details={"system_user": system_user}
            )

        record = data[system_user]
        username = record.get("username")
        if not username:
            raise AuthError(
                message="Credencial invalida: falta username",
                details={"system_user": system_user}
            )

        if record.get("password_encrypted"):
            try:
                password = SecretProtector.decrypt(record["password_encrypted"])
            except Exception as e:
                raise AuthError(
                    message="No fue posible desencriptar password del usuario",
                    details={"system_user": system_user, "error": str(e)}
                )
        else:
            password = record.get("password")

        if not password:
            raise AuthError(
                message="Credencial invalida: falta password",
                details={"system_user": system_user}
            )

        return {"username": username, "password": password}
