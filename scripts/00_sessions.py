# scripts/00_sessions.py
# ================================================================
# Script para configurar credenciales y obtener API Key de Charly.io
# 
# DESCRIPCIÓN:
# Este script permite:
# 1. Crear archivos JSON vacíos con la estructura correcta
# 2. Ingresar credenciales de usuario (username/password)
# 3. Guardar credenciales en _charly_secrets/charly_users.json
# 4. Realizar login y obtener API key
# 5. Guardar API key en _charly_secrets/api_keys.json
#
# USO:
#   python scripts/00_sessions.py
# ================================================================

import sys
import json
from pathlib import Path
from datetime import datetime

# ⬇️ Fuerza la carpeta donde están core/, services/, orchestration/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from security.user_resolver import SystemUserResolver
from security.paths import get_credential_store_path, get_api_key_store_path
from core.auth import CharlyAuth
from config.config_loader import ConfigLoader
from core.exceptions import AuthError

# ------------------------------------------------------------------
# FUNCIONES AUXILIARES
# ------------------------------------------------------------------

def create_empty_json_files():
    """
    Crea los archivos JSON vacíos con la estructura correcta.
    """
    # Crear directorio si no existe
    secrets_dir = PROJECT_ROOT / "_charly_secrets"
    secrets_dir.mkdir(parents=True, exist_ok=True)
    
    # Crear charly_users.json vacío
    users_file = get_credential_store_path()
    if not users_file.exists():
        users_file.write_text("{}", encoding="utf-8")
        print(f"[OK] Archivo creado: {users_file}")
    else:
        print(f"[INFO] Archivo ya existe: {users_file}")
    
    # Crear api_keys.json vacío
    api_keys_file = get_api_key_store_path()
    if not api_keys_file.exists():
        api_keys_file.write_text("{}", encoding="utf-8")
        print(f"[OK] Archivo creado: {api_keys_file}")
    else:
        print(f"[INFO] Archivo ya existe: {api_keys_file}")

def load_credentials_file() -> dict:
    """
    Carga el archivo de credenciales.
    """
    users_file = get_credential_store_path()
    try:
        content = users_file.read_text(encoding="utf-8").strip()
        return json.loads(content) if content else {}
    except json.JSONDecodeError:
        return {}

def save_credentials(system_user: str, username: str, password: str):
    """
    Guarda las credenciales en charly_users.json
    """
    users_file = get_credential_store_path()
    data = load_credentials_file()
    
    data[system_user] = {
        "username": username,
        "password": password
    }
    
    users_file.write_text(
        json.dumps(data, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"[OK] Credenciales guardadas para usuario: {system_user}")

def load_api_keys_file() -> dict:
    """
    Carga el archivo de API keys.
    """
    api_keys_file = get_api_key_store_path()
    try:
        content = api_keys_file.read_text(encoding="utf-8").strip()
        return json.loads(content) if content else {}
    except json.JSONDecodeError:
        return {}

def save_api_key(system_user: str, api_key: str):
    """
    Guarda el API key en api_keys.json
    """
    api_keys_file = get_api_key_store_path()
    data = load_api_keys_file()
    
    data[system_user] = {
        "api_key": api_key,
        "updated_at": datetime.utcnow().isoformat()
    }
    
    api_keys_file.write_text(
        json.dumps(data, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"[OK] API key guardada para usuario: {system_user}")

# ------------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# ------------------------------------------------------------------

def main():
    print("=" * 80)
    print("CONFIGURACIÓN DE CREDENCIALES Y API KEY - CHARLY.IO")
    print("=" * 80)
    print()
    
    # 1. Crear archivos JSON vacíos
    print(">> Paso 1: Creando archivos JSON vacíos...")
    create_empty_json_files()
    print()
    
    # 2. Obtener usuario del sistema
    print(">> Paso 2: Detectando usuario del sistema...")
    system_info = SystemUserResolver.resolve()
    system_user = system_info["system_user"]
    print(f"[OK] Usuario del sistema: {system_user}")
    print()
    
    # 3. Verificar si ya existen credenciales
    existing_credentials = load_credentials_file()
    if system_user in existing_credentials:
        print(f"[INFO] Ya existen credenciales para el usuario: {system_user}")
        use_existing = input("¿Desea usar las credenciales existentes? [S/n]: ").strip().lower()
        if use_existing != "n":
            username = existing_credentials[system_user]["username"]
            password = existing_credentials[system_user]["password"]
            print(f"[OK] Usando credenciales existentes para: {username}")
        else:
            # Solicitar nuevas credenciales
            print("\n>> Ingrese nuevas credenciales:")
            username = input("Username (email): ").strip()
            password = input("Password: ").strip()
            save_credentials(system_user, username, password)
    else:
        # Solicitar credenciales
        print(">> Paso 3: Ingrese sus credenciales de Charly.io")
        username = input("Username (email): ").strip()
        if not username:
            print("[ERROR] El username no puede estar vacío")
            sys.exit(1)
        
        password = input("Password: ").strip()
        if not password:
            print("[ERROR] El password no puede estar vacío")
            sys.exit(1)
        
        save_credentials(system_user, username, password)
    
    print()
    
    # 4. Cargar configuración
    print(">> Paso 4: Cargando configuración...")
    config_loader = ConfigLoader(Path("config/charly.yaml"))
    
    # Obtener environment (default: prod)
    env = config_loader.get("charly", "environment", default="prod")
    
    # Obtener base_url según el environment
    base_url = config_loader.get("charly", "base_url", env)
    
    # Obtener timeout
    timeout = config_loader.get("charly", "http", "timeout_seconds", default=30)
    
    if not base_url:
        print(f"[ERROR] No se pudo cargar base_url desde la configuración")
        print(f"Environment: {env}")
        sys.exit(1)
    
    print(f"[OK] Environment: {env}")
    print(f"[OK] Base URL: {base_url}")
    print()
    
    # 5. Realizar login
    print(">> Paso 5: Realizando login en Charly.io...")
    try:
        auth = CharlyAuth(base_url=base_url, timeout=timeout)
        api_key = auth.create_session(username=username, password=password)
        print(f"[OK] Login exitoso!")
        print(f"[OK] API Key obtenida: {api_key[:20]}...")
    except AuthError as e:
        print(f"[ERROR] Error de autenticación: {e.message}")
        if hasattr(e, 'details'):
            print(f"Detalles: {e.details}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Error inesperado: {str(e)}")
        sys.exit(1)
    
    print()
    
    # 6. Guardar API key
    print(">> Paso 6: Guardando API key...")
    save_api_key(system_user, api_key)
    print()
    
    # 7. Resumen final
    print("=" * 80)
    print("CONFIGURACIÓN COMPLETADA")
    print("=" * 80)
    print()
    print(f"Usuario del sistema: {system_user}")
    print(f"Usuario Charly: {username}")
    print(f"API Key guardada: {api_key[:20]}...")
    print()
    print("Archivos creados/modificados:")
    print(f"  - {get_credential_store_path()}")
    print(f"  - {get_api_key_store_path()}")
    print()
    print("Ahora puede usar el Bootstrap para inicializar el cliente:")
    print("  from orchestration.bootstrap import Bootstrap")
    print("  ctx = Bootstrap(config_path=Path('config/charly.yaml')).run()")

if __name__ == "__main__":
    main()
