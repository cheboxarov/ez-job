"""Use case для отклика на вакансию с сохранением в БД."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from loguru import logger

from domain.entities.vacancy_response import VacancyResponse
from domain.exceptions.subscription_limit_exceeded import SubscriptionLimitExceededError
from domain.use_cases.create_vacancy_response import CreateVacancyResponseUseCase
from domain.use_cases.respond_to_vacancy import RespondToVacancyUseCase
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase
from domain.use_cases.check_and_update_subscription import (
    CheckAndUpdateSubscriptionUseCase,
)
from domain.use_cases.increment_response_count import IncrementResponseCountUseCase


class RespondToVacancyAndSaveUseCase:
    """Use case для отклика на вакансию в HeadHunter с сохранением в БД.

    Составной use case, который:
    1. Отправляет отклик на вакансию через HH API (RespondToVacancyUseCase)
    2. Если отклик успешен, сохраняет его в БД (CreateVacancyResponseUseCase)
    """

    def __init__(
        self,
        respond_to_vacancy_uc: RespondToVacancyUseCase,
        create_vacancy_response_uc: CreateVacancyResponseUseCase,
        check_subscription_uc: CheckAndUpdateSubscriptionUseCase | None = None,
        increment_response_count_uc: IncrementResponseCountUseCase | None = None,
    ) -> None:
        """Инициализация use case.

        Args:
            respond_to_vacancy_uc: Use case для отправки отклика через HH API.
            create_vacancy_response_uc: Use case для сохранения отклика в БД.
            check_subscription_uc: Use case для проверки и обновления подписки (опционально).
            increment_response_count_uc: Use case для инкремента счетчика откликов (опционально).
        """
        self._respond_to_vacancy_uc = respond_to_vacancy_uc
        self._create_vacancy_response_uc = create_vacancy_response_uc
        self._check_subscription_uc = check_subscription_uc
        self._increment_response_count_uc = increment_response_count_uc

    async def execute(
        self,
        *,
        vacancy_id: int,
        resume_id: UUID,
        user_id: UUID,
        resume_hash: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        letter: str = "1",
        vacancy_name: str,
        vacancy_url: str | None = None,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        update_cookies_uc: Optional[UpdateUserHhAuthCookiesUseCase] = None,
        test_answers: Dict[str, str | List[str]] | None = None,
        test_metadata: Dict[str, str] | None = None,
    ) -> Dict[str, Any]:
        """Откликнуться на вакансию и сохранить отклик в БД.

        Args:
            vacancy_id: ID вакансии в HH.
            resume_id: ID резюме, с которого делается отклик.
            user_id: ID пользователя, который делает отклик.
            resume_hash: Hash резюме в HH.
            headers: HTTP заголовки для запроса к HH API.
            cookies: HTTP cookies для запроса к HH API.
            letter: Текст сопроводительного письма (по умолчанию "1").
            vacancy_name: Название вакансии.
            vacancy_url: URL вакансии (опционально).
            internal_api_base_url: Базовый URL внутреннего API HH.
            test_answers: Ответы на вопросы теста (ключ - field_name, значение - ответ).
            test_metadata: Метаданные теста (uidPk, guid, startTime, testRequired).

        Returns:
            Ответ от API HH после отклика.

        Raises:
            Exception: При ошибках отправки отклика в HH API.
            SubscriptionLimitExceededError: При превышении лимита откликов.
        """
        # 1. Проверяем лимит подписки перед отправкой отклика
        if self._check_subscription_uc is not None:
            try:
                user_subscription, plan = await self._check_subscription_uc.execute(
                    str(user_id)
                )

                # Проверяем, не превышен ли лимит
                if user_subscription.responses_count >= plan.response_limit:
                    # Вычисляем время до сброса
                    seconds_until_reset = None
                    if user_subscription.period_started_at is not None:
                        now = datetime.now(timezone.utc)
                        elapsed = (now - user_subscription.period_started_at).total_seconds()
                        seconds_until_reset = max(0, int(plan.reset_period_seconds - elapsed))

                    raise SubscriptionLimitExceededError(
                        count=user_subscription.responses_count,
                        limit=plan.response_limit,
                        seconds_until_reset=seconds_until_reset,
                    )
            except ValueError as exc:
                # Если подписка не найдена, логируем и продолжаем (для обратной совместимости)
                logger.warning(
                    f"Не удалось проверить лимит подписки для user_id={user_id}: {exc}. "
                    "Продолжаем без проверки лимита."
                )

        # 2. Отправляем отклик в HH через существующий use case
        try:
            hh_response = await self._respond_to_vacancy_uc.execute(
                vacancy_id=vacancy_id,
                resume_hash=resume_hash,
                headers=headers,
                cookies=cookies,
                letter=letter,
                internal_api_base_url=internal_api_base_url,
                user_id=user_id,
                update_cookies_uc=update_cookies_uc,
                test_answers=test_answers,
                test_metadata=test_metadata,
            )
        except Exception as exc:
            logger.error(
                f"Ошибка при отправке отклика на вакансию vacancy_id={vacancy_id}, "
                f"resume_id={resume_id}, user_id={user_id}: {exc}",
                exc_info=True,
            )
            raise

        # 2. Если отклик успешен, сохраняем его в БД
        try:
            logger.info(
                f"Создание VacancyResponse для сохранения: vacancy_id={vacancy_id}, "
                f"resume_id={resume_id}, resume_hash={resume_hash}, user_id={user_id}"
            )
            vacancy_response = VacancyResponse(
                id=uuid4(),
                vacancy_id=vacancy_id,
                resume_id=resume_id,
                resume_hash=resume_hash,
                user_id=user_id,
                cover_letter=letter,
                vacancy_name=vacancy_name,
                vacancy_url=vacancy_url,
                created_at=datetime.utcnow(),
            )
            await self._create_vacancy_response_uc.execute(vacancy_response)
            logger.info(
                f"Успешно сохранен отклик в БД vacancy_id={vacancy_id}, "
                f"resume_id={resume_id}, resume_hash={resume_hash}, user_id={user_id}"
            )

            # 3. Увеличиваем счетчик откликов в подписке
            if self._increment_response_count_uc is not None:
                try:
                    await self._increment_response_count_uc.execute(user_id)
                except ValueError as exc:
                    # Если подписка не найдена, логируем и продолжаем
                    logger.warning(
                        f"Не удалось увеличить счетчик откликов для user_id={user_id}: {exc}"
                    )
        except Exception as exc:
            # Если сохранение в БД не удалось, но отклик уже отправлен в HH,
            # логируем ошибку, но не бросаем исключение
            logger.error(
                f"Ошибка при сохранении отклика в БД (отклик уже отправлен в HH) "
                f"vacancy_id={vacancy_id}, resume_id={resume_id}, user_id={user_id}: {exc}",
                exc_info=True,
            )

        return hh_response
