"""Use case для "касания" резюме на HeadHunter через edit endpoint с пустым телом."""

from __future__ import annotations

from typing import Dict
from uuid import UUID

from loguru import logger

from domain.interfaces.hh_client_port import HHClientPort
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase


class TouchHHResumeEditUseCase:
    """Use case для отправки пустого запроса на редактирование резюме на HeadHunter.
    
    Используется для "касания" резюме через edit endpoint без изменения данных.
    Может быть полезно для обновления метаданных или триггера каких-то процессов на стороне HH.
    """

    def __init__(
        self,
        hh_client: HHClientPort,
    ) -> None:
        """Инициализация use case.

        Args:
            hh_client: Клиент для работы с HeadHunter API.
        """
        self._hh_client = hh_client

    async def execute(
        self,
        *,
        resume_hash: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        hhtm_source: str = "resume_partial_edit",
        user_id: UUID | None = None,
        update_cookies_uc: UpdateUserHhAuthCookiesUseCase | None = None,
    ) -> Dict:
        """Отправить пустой запрос на редактирование резюме на HeadHunter.

        Args:
            resume_hash: Hash резюме.
            headers: Заголовки для запроса к HH API.
            cookies: Куки для запроса к HH API.
            internal_api_base_url: Базовый URL внутреннего API HH.
            hhtm_source: Источник запроса (по умолчанию "resume_partial_edit").
            user_id: UUID пользователя для обновления cookies (опционально).
            update_cookies_uc: Use case для обновления cookies (опционально).

        Returns:
            Dict с результатом запроса.
        """
        # Отправляем запрос с пустым телом (пустой список experience)
        result = await self._hh_client.edit_resume(
            resume_hash=resume_hash,
            experience=[],  # Пустой список опыта работы
            headers=headers,
            cookies=cookies,
            internal_api_base_url=internal_api_base_url,
            hhtm_source=hhtm_source,
            return_cookies=True,
        )

        result_data, updated_cookies = result

        # Обновляем cookies, если передан use case
        if user_id and update_cookies_uc:
            try:
                await update_cookies_uc.execute(
                    user_id=user_id,
                    updated_cookies=updated_cookies,
                )
                logger.debug(f"Обновлены cookies для пользователя {user_id} после touch резюме")
            except Exception as exc:
                logger.warning(
                    f"Не удалось обновить cookies для пользователя {user_id} после touch резюме: {exc}"
                )

        return result_data
