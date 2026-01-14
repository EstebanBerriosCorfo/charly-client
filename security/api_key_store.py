# security/api_key_store.py
# ================================================================
# Store dinámico de API Keys por usuario del sistema
# ================================================================

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class ApiKeyStore:
    """
    Almacena API Keys de Charly por usuario del sistema.

    - Tolera archivo inexistente
    - Tolera archivo vacío
    - Tolera primer run
    - Mantiene timestamp de actualización
    """

    def __init__(self, path: Path):
        self.path = path

        # Garantiza existencia del archivo
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text("{}", encoding="utf-8")

    # ------------------------------------------------------------------
    # API PÚBLICA
    # ------------------------------------------------------------------
    def save(self, system_user: str, api_key: str) -> None:
        data = self._load_all()

        data[system_user] = {
            "api_key": api_key,
            "updated_at": datetime.utcnow().isoformat()
        }

        self._write_all(data)

    def get(self, system_user: str) -> str | None:
        data = self._load_all()
        record = data.get(system_user)
        return record["api_key"] if record else None

    # ------------------------------------------------------------------
    # HELPERS INTERNOS
    # ------------------------------------------------------------------
    def _load_all(self) -> Dict[str, Any]:
        """
        Carga todo el store de manera segura.
        """
        try:
            content = self.path.read_text(encoding="utf-8").strip()
            return json.loads(content) if content else {}
        except json.JSONDecodeError:
            # Archivo corrupto → fallback seguro
            return {}

    def _write_all(self, data: Dict[str, Any]) -> None:
        """
        Persiste el store completo.
        """
        self.path.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8"
        )