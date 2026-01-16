"""Утилита для генерации login_trust_flags для авторизации в HH."""

from __future__ import annotations

import base64
import json
import time

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.backends import default_backend


def generate_login_trust_flags(public_key_pem: str) -> str:
    """Генерирует login_trust_flags для авторизации в HH.

    Логика: base64(RSA-OAEP-SHA256(publicKey, '{"ts":<Date.now()>}'))

    Args:
        public_key_pem: Публичный RSA ключ в формате PEM (строка).

    Returns:
        Base64-закодированная строка с зашифрованным JSON объектом.

    Raises:
        ValueError: Если публичный ключ невалиден.
        Exception: При ошибках шифрования.
    """
    # Создаем JSON объект с текущим временем в миллисекундах
    timestamp_ms = int(time.time() * 1000)
    json_data = {"ts": timestamp_ms}
    json_string = json.dumps(json_data, separators=(",", ":"))

    try:
        # Загружаем публичный ключ из PEM формата
        public_key_bytes = public_key_pem.encode("utf-8")
        public_key: RSAPublicKey = serialization.load_pem_public_key(
            public_key_bytes, backend=default_backend()
        )

        # Проверяем, что это RSA ключ
        if not isinstance(public_key, RSAPublicKey):
            raise ValueError("Публичный ключ должен быть RSA ключом")

        # Шифруем данные используя RSA-OAEP с SHA256
        encrypted_data = public_key.encrypt(
            json_string.encode("utf-8"),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        # Кодируем в base64
        base64_encoded = base64.b64encode(encrypted_data).decode("utf-8")

        return base64_encoded

    except Exception as e:
        raise ValueError(f"Ошибка при генерации login_trust_flags: {e}") from e
