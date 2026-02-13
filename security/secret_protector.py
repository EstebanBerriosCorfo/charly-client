from __future__ import annotations

import base64
import ctypes
from ctypes import wintypes


class _DataBlob(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_byte)),
    ]


class SecretProtector:
    """
    Protege secretos usando DPAPI de Windows.
    El cifrado queda ligado al usuario del sistema operativo.
    """

    @staticmethod
    def encrypt(secret: str) -> str:
        if secret is None:
            raise ValueError("secret no puede ser None")

        raw = secret.encode("utf-8")
        in_blob = _DataBlob(len(raw), ctypes.cast(ctypes.create_string_buffer(raw), ctypes.POINTER(ctypes.c_byte)))
        out_blob = _DataBlob()

        crypt32 = ctypes.windll.crypt32
        kernel32 = ctypes.windll.kernel32

        # BOOL CryptProtectData(...)
        ok = crypt32.CryptProtectData(
            ctypes.byref(in_blob),
            None,
            None,
            None,
            None,
            0,
            ctypes.byref(out_blob),
        )

        if not ok:
            raise RuntimeError("No fue posible proteger el secreto con DPAPI")

        try:
            protected_bytes = ctypes.string_at(out_blob.pbData, out_blob.cbData)
            return base64.b64encode(protected_bytes).decode("ascii")
        finally:
            if out_blob.pbData:
                kernel32.LocalFree(out_blob.pbData)

    @staticmethod
    def decrypt(protected_secret: str) -> str:
        if not protected_secret:
            raise ValueError("protected_secret no puede estar vacio")

        encrypted_bytes = base64.b64decode(protected_secret.encode("ascii"))
        in_blob = _DataBlob(
            len(encrypted_bytes),
            ctypes.cast(ctypes.create_string_buffer(encrypted_bytes), ctypes.POINTER(ctypes.c_byte)),
        )
        out_blob = _DataBlob()

        crypt32 = ctypes.windll.crypt32
        kernel32 = ctypes.windll.kernel32

        # BOOL CryptUnprotectData(...)
        ok = crypt32.CryptUnprotectData(
            ctypes.byref(in_blob),
            None,
            None,
            None,
            None,
            0,
            ctypes.byref(out_blob),
        )

        if not ok:
            raise RuntimeError("No fue posible desencriptar el secreto con DPAPI")

        try:
            raw = ctypes.string_at(out_blob.pbData, out_blob.cbData)
            return raw.decode("utf-8")
        finally:
            if out_blob.pbData:
                kernel32.LocalFree(out_blob.pbData)
