"""Утилиты для вычисления hash резюме."""

from __future__ import annotations

import hashlib


def calculate_resume_content_hash(resume_content: str) -> str:
    """Вычислить SHA256 hash от содержимого резюме.

    Используется для создания уникального идентификатора резюме,
    который зависит от содержимого и остается стабильным для одинакового содержимого.

    Args:
        resume_content: Текст резюме.

    Returns:
        SHA256 hash от содержимого резюме в hex формате (64 символа).
    """
    hash_obj = hashlib.sha256(resume_content.encode('utf-8'))
    return hash_obj.hexdigest()
