"""Use case для отклика на вакансию в HeadHunter."""

from __future__ import annotations

from typing import Any, Dict, Optional
from uuid import UUID

from loguru import logger

from domain.interfaces.hh_client_port import HHClientPort
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase
from infrastructure.clients.hh_client_with_cookie_update import HHHttpClientWithCookieUpdate


class RespondToVacancyUseCase:
    """Use case для отклика на вакансию в HeadHunter.

    Отправляет отклик на вакансию через внутренний API HH.
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
        vacancy_id: int,
        resume_hash: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        letter: str = "1",
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        user_id: Optional[UUID] = None,
        update_cookies_uc: Optional[UpdateUserHhAuthCookiesUseCase] = None,
        test_answers: Dict[str, str | List[str]] | None = None,
        test_metadata: Dict[str, str] | None = None,
    ) -> Dict[str, Any]:
        """Откликнуться на вакансию.

        Args:
            vacancy_id: ID вакансии в HH.
            resume_hash: Hash резюме в HH.
            headers: HTTP заголовки для запроса к HH API.
            cookies: HTTP cookies для запроса к HH API.
            letter: Текст сопроводительного письма (по умолчанию "1").
            internal_api_base_url: Базовый URL внутреннего API HH.
            user_id: UUID пользователя для обновления cookies (опционально).
            update_cookies_uc: Use case для обновления cookies (опционально).
            test_answers: Ответы на вопросы теста (ключ - field_name, значение - ответ).
            test_metadata: Метаданные теста (uidPk, guid, startTime, testRequired).

        Returns:
            Ответ от API HH после отклика.

        Raises:
            Exception: При ошибках выполнения запроса к HH API.
        """
        # Если передан user_id и update_cookies_uc, используем обертку для автоматического сохранения cookies
        if user_id and update_cookies_uc:
            client = HHHttpClientWithCookieUpdate(self._hh_client, user_id, update_cookies_uc)
        else:
            client = self._hh_client
        try:
            result = await client.respond_to_vacancy(
                vacancy_id=vacancy_id,
                resume_hash=resume_hash,
                headers=headers,
                cookies=cookies,
                letter=letter,
                internal_api_base_url=internal_api_base_url,
                test_answers=test_answers,
                test_metadata=test_metadata,
            )
            logger.info(
                f"Успешно отправлен отклик на вакансию vacancy_id={vacancy_id}, resume_hash={resume_hash}"
            )
            return result
        except Exception as exc:
            logger.error(
                f"Ошибка при отклике на вакансию vacancy_id={vacancy_id}, resume_hash={resume_hash}: {exc}",
                exc_info=True,
            )
            raise
