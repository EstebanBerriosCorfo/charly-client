# security/paths.py
# ================================================================
# Rutas internas del proyecto (secretos y runtime)
# ================================================================

from pathlib import Path


def get_project_root() -> Path:
    """
    Obtiene la raíz del proyecto (donde vive el código).
    """
    # security/paths.py → security → project root
    return Path(__file__).resolve().parents[1]


def get_config_dir() -> Path:
    """
    Carpeta interna de secretos del proyecto.
    """
    path = get_project_root() / "_charly_secrets"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_credential_store_path() -> Path:
    return get_config_dir() / "charly_users.json"


def get_api_key_store_path() -> Path:
    return get_config_dir() / "api_keys.json"

# ----------------------------------------------------------------
# 📥 DESCARGAS / OUTPUTS (NUEVO)
# ----------------------------------------------------------------
def get_downloads_dir() -> Path:
    """
    Carpeta de descargas del proyecto.

    Uso:
    - Exportes a Excel
    - JSON grandes
    - Outputs de scripts (ETL-style)

    Regla:
    - Siempre dentro del proyecto
    - Nunca rutas absolutas del sistema
    """
    path = get_project_root() / "downloads"
    path.mkdir(parents=True, exist_ok=True)
    return path