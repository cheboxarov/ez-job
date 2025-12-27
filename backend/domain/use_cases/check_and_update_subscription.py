"""Use case для проверки и обновления подписки пользователя."""

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


class CheckAndUpdateSubscriptionUseCase:
    """Use case для проверки срока действия подписки и сброса лимита.

    Выполняет две проверки:
    1. Проверка срока действия подписки (expires_at) - если истек, даунгрейд на FREE
    2. Проверка периода сброса лимита (reset_period) - если прошло, сброс счетчика
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

    async def execute(self, user_id: UUID) -> tuple[UserSubscription, SubscriptionPlan]:
        """Проверить и обновить подписку пользователя.

        Args:
            user_id: UUID пользователя.

        Returns:
            Кортеж из обновленной подписки и текущего плана.

        Raises:
            ValueError: Если подписка не найдена.
        """
        # Получаем подписку пользователя
        user_subscription = await self._user_subscription_repository.get_by_user_id(
            user_id
        )
        # Если подписки ещё нет — создаём FREE по умолчанию (get or create).
        if user_subscription is None:
            now = datetime.now(timezone.utc)
            free_plan = await self._subscription_plan_repository.get_by_name("FREE")
            if free_plan is None:
                raise ValueError("FREE план не найден в БД")

            user_subscription = UserSubscription(
                user_id=user_id,
                subscription_plan_id=free_plan.id,
                responses_count=0,
                # Старт периода и подписки ставим на сейчас,
                # чтобы корректно работали расчёты лимитов.
                period_started_at=now,
                started_at=now,
                expires_at=None,
            )
            user_subscription = await self._user_subscription_repository.create(
                user_subscription
            )

            logger.info(
                "Создана новая подписка FREE для пользователя {user_id}. "
                "response_limit={response_limit}",
                user_id=user_id,
                response_limit=free_plan.response_limit,
            )
            return user_subscription, free_plan

        # Получаем текущий план
        plan = await self._subscription_plan_repository.get_by_id(
            user_subscription.subscription_plan_id
        )
        if plan is None:
            raise ValueError(
                f"План подписки {user_subscription.subscription_plan_id} не найден"
            )

        now = datetime.now(timezone.utc)
        updated = False

        # Шаг 1: Проверка срока действия подписки
        if user_subscription.expires_at is not None and now > user_subscription.expires_at:
            # Подписка истекла - даунгрейд на FREE
            logger.info(
                f"Подписка пользователя {user_id} истекла. "
                f"Текущий план: {plan.name}, даунгрейд на FREE"
            )

            free_plan = await self._subscription_plan_repository.get_by_name("FREE")
            if free_plan is None:
                raise ValueError("FREE план не найден в БД")

            # Мягкое приземление: сбрасываем счетчики
            user_subscription.subscription_plan_id = free_plan.id
            user_subscription.started_at = now
            user_subscription.expires_at = None
            user_subscription.responses_count = 0
            user_subscription.period_started_at = None
            updated = True
            plan = free_plan

            logger.info(
                f"Пользователь {user_id} переведен на FREE план. "
                f"Счетчики сброшены."
            )

        # Шаг 2: Проверка периода сброса лимита
        if user_subscription.period_started_at is not None:
            elapsed = (now - user_subscription.period_started_at).total_seconds()

            if elapsed >= plan.reset_period_seconds:
                # Период истек - сбрасываем лимит
                logger.info(
                    f"Период лимита для пользователя {user_id} истек. "
                    f"Прошло {elapsed:.0f} секунд, требуется {plan.reset_period_seconds}. "
                    f"Сброс счетчика с {user_subscription.responses_count} на 0"
                )

                user_subscription.responses_count = 0
                user_subscription.period_started_at = now
                updated = True

        # Сохраняем изменения, если были обновления
        if updated:
            user_subscription = await self._user_subscription_repository.update(
                user_subscription
            )

        return user_subscription, plan
