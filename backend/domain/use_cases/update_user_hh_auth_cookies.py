"""Use case для обновления cookies пользователя после запросов к HH API."""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict
from uuid import UUID

from loguru import logger

from domain.entities.user_hh_auth_data import UserHhAuthData
from domain.interfaces.user_hh_auth_data_repository_port import (
    UserHhAuthDataRepositoryPort,
)

# region agent log
def _debug_log(hypothesis_id: str, location: str, message: str, data: dict) -> None:
    try:
        Path("/Users/apple/dev/hh/.cursor/debug.log").open("a", encoding="utf-8").write(
            json.dumps(
                {
                    "sessionId": "hh-deadlock",
                    "runId": "pre-fix",
                    "hypothesisId": hypothesis_id,
                    "location": location,
                    "message": message,
                    "data": data,
                    "pid": os.getpid(),
                    "process": sys.argv[0] if sys.argv else None,
                    "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
                },
                ensure_ascii=False,
            )
            + "\n"
        )
    except Exception:
        # не ломаем основной флоу
        pass
# endregion


class UpdateUserHhAuthCookiesUseCase:
    """Use case для обновления HH auth cookies пользователя.

    Объединяет новые cookies с существующими (новые перезаписывают старые)
    и сохраняет обновленные данные в БД.
    """

    def __init__(self, repository: UserHhAuthDataRepositoryPort) -> None:
        """Инициализация use case.

        Args:
            repository: Репозиторий для работы с HH auth данными пользователя.
        """
        self._repository = repository

    async def execute(
        self,
        user_id: UUID,
        updated_cookies: Dict[str, str],
        headers: Dict[str, str] | None = None,
    ) -> UserHhAuthData:
        """Обновить cookies пользователя после запроса к HH API.

        Args:
            user_id: UUID пользователя.
            updated_cookies: Словарь обновленных cookies из ответа HH API.
            headers: Опциональные обновленные headers. Если не переданы,
                используются существующие headers.

        Returns:
            Обновленная доменная сущность UserHhAuthData.

        Raises:
            ValueError: Если auth данные для пользователя не найдены.
        """
        debounce_seconds = 15 * 60
        started = time.perf_counter()
        _debug_log(
            "H1",
            "update_user_hh_auth_cookies.execute:enter",
            "cookie update requested",
            {
                "user_id": str(user_id),
                "updated_cookie_keys_count": len(updated_cookies),
                "has_headers": headers is not None,
            },
        )
        # Быстрый путь: читаем текущее состояние БЕЗ блокировки.
        # Если мы недавно уже сохраняли cookies в БД, то пропускаем запись (debounce 15 минут),
        # чтобы не создавать конкурирующие транзакции между воркерами и API.
        current_auth = await self._repository.get_by_user_id(user_id, with_for_update=False)
        if current_auth is None:
            raise ValueError(
                f"HH auth data not found for user_id={user_id}. "
                "Please set auth data first."
            )

        now = datetime.now(timezone.utc)
        if current_auth.cookies_updated_at is not None:
            last = current_auth.cookies_updated_at
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            age_seconds = (now - last).total_seconds()
            if age_seconds < debounce_seconds:
                _debug_log(
                    "H6",
                    "update_user_hh_auth_cookies.execute:debounced",
                    "skip DB write due to debounce window",
                    {
                        "user_id": str(user_id),
                        "age_seconds": int(age_seconds),
                        "debounce_seconds": debounce_seconds,
                    },
                )
                return current_auth

        # Медленный путь: пора записывать в БД — берём блокировки (advisory + FOR UPDATE)
        # и повторно читаем состояние под lock, чтобы корректно смержить cookies.
        _debug_log(
            "H2",
            "update_user_hh_auth_cookies.execute:before_for_update",
            "about to SELECT FOR UPDATE user auth row",
            {"user_id": str(user_id)},
        )
        current_auth = await self._repository.get_by_user_id(user_id, with_for_update=True)
        _debug_log(
            "H2",
            "update_user_hh_auth_cookies.execute:after_for_update",
            "SELECT FOR UPDATE completed",
            {"user_id": str(user_id), "elapsed_ms": int((time.perf_counter() - started) * 1000)},
        )
        if current_auth is None:
            raise ValueError(
                f"HH auth data not found for user_id={user_id}. "
                "Please set auth data first."
            )

        # Объединить cookies (новые перезаписывают старые)
        # Важно: сохраняем все существующие cookies, обновляем только те, что пришли в ответе
        merged_cookies = {**current_auth.cookies, **updated_cookies}

        # Обновить headers если переданы, иначе использовать существующие
        final_headers = headers if headers is not None else current_auth.headers

        # Сохранить через upsert
        _debug_log(
            "H3",
            "update_user_hh_auth_cookies.execute:before_upsert",
            "about to UPDATE user cookies",
            {"user_id": str(user_id)},
        )
        updated_auth = await self._repository.upsert(
            user_id=user_id,
            headers=final_headers,
            cookies=merged_cookies,
        )
        _debug_log(
            "H3",
            "update_user_hh_auth_cookies.execute:after_upsert",
            "UPDATE user cookies completed",
            {"user_id": str(user_id), "elapsed_ms": int((time.perf_counter() - started) * 1000)},
        )

        logger.debug(
            f"Updated HH auth cookies for user_id={user_id}. "
            f"Cookies updated: {len(updated_cookies)} keys"
        )

        return updated_auth
