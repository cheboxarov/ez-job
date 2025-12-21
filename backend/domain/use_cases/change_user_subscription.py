"""Use case для смены плана подписки пользователя."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from loguru import logger

from domain.entities.subscription_plan import SubscriptionPlan
from domain.entities.user_subscription import UserSubscription
from domain.interfaces.subscription_plan_repository_port import (
    SubscriptionPlanRepositoryPort,
)
from domain.interfaces.user_subscription_repository_port import (
    UserSubscriptionRepositoryPort,
)


class ChangeUserSubscriptionUseCase:
    """Use case для смены плана подписки пользователя.

    Позволяет пользователю выбрать новый тарифный план.
    При смене плана:
    - Обновляется subscription_plan_id
    - Сбрасываются счетчики откликов
    - Обновляется срок действия подписки
    - Устанавливается новая дата начала периода сброса
    """

    def __init__(
        self,
        user_subscription_repository: UserSubscriptionRepositoryPort,
        subscription_plan_repository: SubscriptionPlanRepositoryPort,
    ) -> None:
        """Инициализация use case.

        Args:
            user_subscription_repository: Репозиторий подписок пользователей.
            subscription_plan_repository: Репозиторий планов подписки.
        """
        self._user_subscription_repository = user_subscription_repository
        self._subscription_plan_repository = subscription_plan_repository

    async def execute(
        self, user_id: UUID, plan_name: str
    ) -> tuple[UserSubscription, SubscriptionPlan]:
        """Изменить план подписки пользователя.

        Args:
            user_id: UUID пользователя.
            plan_name: Название нового плана (FREE, PLAN_1, PLAN_2, PLAN_3).

        Returns:
            Кортеж из обновленной подписки и нового плана.

        Raises:
            ValueError: Если план с указанным именем не найден.
        """
        # Получаем план по имени
        plan = await self._subscription_plan_repository.get_by_name(plan_name)
        if plan is None:
            raise ValueError(f"План подписки '{plan_name}' не найден")

        # Получаем текущую подписку пользователя
        user_subscription = await self._user_subscription_repository.get_by_user_id(
            user_id
        )

        now = datetime.now(timezone.utc)

        if user_subscription is None:
            # Подписка не существует - создаем новую
            logger.info(
                f"Создание новой подписки для пользователя {user_id} с планом {plan_name}"
            )

            # Вычисляем срок действия подписки
            expires_at = None
            if plan.duration_days > 0:
                expires_at = now + timedelta(days=plan.duration_days)

            user_subscription = UserSubscription(
                user_id=user_id,
                subscription_plan_id=plan.id,
                responses_count=0,
                period_started_at=now,
                started_at=now,
                expires_at=expires_at,
            )

            user_subscription = await self._user_subscription_repository.create(
                user_subscription
            )

            logger.info(
                f"Подписка создана для пользователя {user_id}, план: {plan_name}, "
                f"expires_at: {expires_at}"
            )
        else:
            # Подписка существует - обновляем план
            old_plan_id = user_subscription.subscription_plan_id
            logger.info(
                f"Смена плана подписки для пользователя {user_id}: "
                f"старый план {old_plan_id}, новый план {plan_name}"
            )

            # Обновляем план
            user_subscription.subscription_plan_id = plan.id

            # Сбрасываем счетчики
            user_subscription.responses_count = 0
            user_subscription.period_started_at = now

            # Обновляем срок действия подписки
            if plan.name == "FREE":
                # FREE план - бессрочная подписка
                user_subscription.expires_at = None
            elif plan.duration_days > 0:
                # Если у плана есть срок действия, устанавливаем его
                user_subscription.expires_at = now + timedelta(days=plan.duration_days)
            else:
                # Если duration_days = 0, делаем подписку бессрочной
                user_subscription.expires_at = None

            # Обновляем дату начала подписки только если она еще не установлена
            # или если мы переходим с FREE на платный план
            if user_subscription.started_at is None:
                user_subscription.started_at = now

            user_subscription = await self._user_subscription_repository.update(
                user_subscription
            )

            logger.info(
                f"План подписки изменен для пользователя {user_id}, новый план: {plan_name}, "
                f"expires_at: {user_subscription.expires_at}"
            )

        return user_subscription, plan

