"""Use case для инкремента счетчика откликов пользователя."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from loguru import logger

from domain.entities.user_subscription import UserSubscription
from domain.interfaces.user_subscription_repository_port import (
    UserSubscriptionRepositoryPort,
)
from domain.use_cases.check_and_update_subscription import (
    CheckAndUpdateSubscriptionUseCase,
)


class IncrementResponseCountUseCase:
    """Use case для увеличения счетчика откликов пользователя.

    Перед инкрементом проверяет и обновляет подписку (срок действия, сброс лимита).
    Если счетчик был 0 и период не начат - устанавливает начало периода.
    """

    def __init__(
        self,
        check_subscription_uc: CheckAndUpdateSubscriptionUseCase,
        user_subscription_repository: UserSubscriptionRepositoryPort,
    ) -> None:
        """Инициализация use case.

        Args:
            check_subscription_uc: Use case для проверки и обновления подписки.
            user_subscription_repository: Репозиторий подписок пользователей.
        """
        self._check_subscription_uc = check_subscription_uc
        self._user_subscription_repository = user_subscription_repository

    async def execute(self, user_id: UUID) -> UserSubscription:
        """Увеличить счетчик откликов пользователя.

        Args:
            user_id: UUID пользователя.

        Returns:
            Обновленная подписка пользователя.

        Raises:
            ValueError: Если подписка не найдена.
        """
        # Проверяем и обновляем подписку (срок действия, сброс лимита)
        user_subscription, _ = await self._check_subscription_uc.execute(user_id)

        # Если счетчик был 0 и период не начат - начинаем период
        if user_subscription.responses_count == 0 and user_subscription.period_started_at is None:
            user_subscription.period_started_at = datetime.now(timezone.utc)
            logger.info(
                f"Начало нового периода для пользователя {user_id}. "
                f"period_started_at установлен"
            )

        # Увеличиваем счетчик
        user_subscription.responses_count += 1

        logger.info(
            f"Счетчик откликов пользователя {user_id} увеличен. "
            f"Новое значение: {user_subscription.responses_count}"
        )

        # Сохраняем изменения
        return await self._user_subscription_repository.update(user_subscription)
