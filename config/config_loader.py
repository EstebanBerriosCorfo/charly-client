# config/config_loader.py
# ================================================================
# Loader de configuración YAML del sistema
# ================================================================

from pathlib import Path
import yaml
from core.exceptions import CharlyApiError


class ConfigLoader:

    def __init__(self, path: Path):
        if not path.exists():
            raise CharlyApiError(
                message="Archivo de configuración no encontrado",
                details={"path": str(path)}
            )

        self.config = yaml.safe_load(path.read_text(encoding="utf-8"))

    def get(self, *keys, default=None):
        node = self.config
        for key in keys:
            node = node.get(key)
            if node is None:
                return default
        return node