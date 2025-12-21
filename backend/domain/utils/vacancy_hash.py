"""Утилиты для вычисления hash вакансий."""

from __future__ import annotations

import hashlib


def calculate_vacancy_hash(vacancy_id: int) -> str:
    """Вычислить hash от vacancy_id.

    Используется для создания уникального идентификатора вакансии,
    который не зависит от содержимого вакансии и остается стабильным.

    Args:
        vacancy_id: ID вакансии в HH.

    Returns:
        SHA256 hash от строкового представления vacancy_id в hex формате.
    """
    vacancy_id_str = str(vacancy_id)
    hash_obj = hashlib.sha256(vacancy_id_str.encode('utf-8'))
    return hash_obj.hexdigest()
