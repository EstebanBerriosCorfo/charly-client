# security/user_resolver.py
# ================================================================
# Resolución del usuario del sistema operativo
# ================================================================

import getpass
import socket


class SystemUserResolver:

    #===========================================================
    # Resolución del usuario del sistema operativo
    #===========================================================

    @staticmethod
    def resolve() -> dict:
        return {
            "system_user": getpass.getuser(),
            "hostname": socket.gethostname(),
        }