"""Реализация репозитория подписок пользователей."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.user_subscription import UserSubscription
from domain.interfaces.user_subscription_repository_port import (
    UserSubscriptionRepositoryPort,
)
from infrastructure.database.models.user_subscription_model import UserSubscriptionModel


class UserSubscriptionRepository(UserSubscriptionRepositoryPort):
    """Реализация репозитория подписок пользователей для SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория.

        Args:
            session: Async сессия SQLAlchemy.
        """
        self._session = session

    async def get_by_user_id(self, user_id: UUID) -> UserSubscription | None:
        """Получить подписку пользователя по user_id.

        Args:
            user_id: UUID пользователя.

        Returns:
            Доменная сущность UserSubscription или None, если не найдено.
        """
        stmt = select(UserSubscriptionModel).where(
            UserSubscriptionModel.user_id == user_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def create(self, user_subscription: UserSubscription) -> UserSubscription:
        """Создать подписку пользователя.

        Args:
            user_subscription: Доменная сущность UserSubscription для создания.

        Returns:
            Созданная доменная сущность UserSubscription.
        """
        model = UserSubscriptionModel(
            user_id=user_subscription.user_id,
            subscription_plan_id=user_subscription.subscription_plan_id,
            responses_count=user_subscription.responses_count,
            period_started_at=user_subscription.period_started_at,
            started_at=user_subscription.started_at,
            expires_at=user_subscription.expires_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def update(self, user_subscription: UserSubscription) -> UserSubscription:
        """Обновить подписку пользователя.

        Args:
            user_subscription: Доменная сущность UserSubscription с обновленными данными.

        Returns:
            Обновленная доменная сущность UserSubscription.

        Raises:
            ValueError: Если подписка с таким user_id не найдена.
        """
        stmt = select(UserSubscriptionModel).where(
            UserSubscriptionModel.user_id == user_subscription.user_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            raise ValueError(
                f"Подписка для пользователя {user_subscription.user_id} не найдена"
            )

        model.subscription_plan_id = user_subscription.subscription_plan_id
        model.responses_count = user_subscription.responses_count
        model.period_started_at = user_subscription.period_started_at
        model.started_at = user_subscription.started_at
        model.expires_at = user_subscription.expires_at

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    def _to_domain(self, model: UserSubscriptionModel) -> UserSubscription:
        """Преобразовать SQLAlchemy модель в доменную сущность.

        Args:
            model: SQLAlchemy модель UserSubscriptionModel.

        Returns:
            Доменная сущность UserSubscription.
        """
        return UserSubscription(
            user_id=model.user_id,
            subscription_plan_id=model.subscription_plan_id,
            responses_count=model.responses_count,
            period_started_at=model.period_started_at,
            started_at=model.started_at,
            expires_at=model.expires_at,
        )
