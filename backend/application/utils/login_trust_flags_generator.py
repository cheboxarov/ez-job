"""Утилита для генерации login_trust_flags для авторизации в HH.

DEPRECATED: Этот модуль оставлен для обратной совместимости.
Используйте domain.utils.login_trust_flags_generator напрямую.
"""

from domain.utils.login_trust_flags_generator import generate_login_trust_flags

__all__ = ["generate_login_trust_flags"]

