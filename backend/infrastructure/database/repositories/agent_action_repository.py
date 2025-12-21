"""Реализация репозитория действий агента."""

from __future__ import annotations

from typing import List
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.agent_action import AgentAction
from domain.interfaces.agent_action_repository_port import AgentActionRepositoryPort
from infrastructure.database.models.agent_action_model import AgentActionModel


class AgentActionRepository(AgentActionRepositoryPort):
    """Реализация репозитория действий агента для SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория.

        Args:
            session: Async сессия SQLAlchemy.
        """
        self._session = session

    async def create(self, action: AgentAction) -> AgentAction:
        """Создать действие агента.

        Args:
            action: Доменная сущность AgentAction для создания.
                   Поле id может быть не заполнено (будет сгенерировано).

        Returns:
            Созданная доменная сущность AgentAction с заполненными id, created_at и updated_at.
        """
        # Генерируем ID, если не указан
        action_id = action.id if action.id else uuid4()

        model = AgentActionModel(
            id=action_id,
            type=action.type,
            entity_type=action.entity_type,
            entity_id=action.entity_id,
            created_by=action.created_by,
            data=action.data,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def list(
        self,
        *,
        type: str | None = None,
        entity_type: str | None = None,
        entity_id: int | None = None,
        created_by: str | None = None,
    ) -> List[AgentAction]:
        """Получить список действий с опциональной фильтрацией.

        Args:
            type: Фильтр по типу действия.
            entity_type: Фильтр по типу сущности.
            entity_id: Фильтр по ID сущности.
            created_by: Фильтр по идентификатору агента.

        Returns:
            Список доменных сущностей AgentAction, отсортированный по created_at (desc).
        """
        stmt = select(AgentActionModel)

        # Динамически добавляем фильтры
        if type is not None:
            stmt = stmt.where(AgentActionModel.type == type)
        if entity_type is not None:
            stmt = stmt.where(AgentActionModel.entity_type == entity_type)
        if entity_id is not None:
            stmt = stmt.where(AgentActionModel.entity_id == entity_id)
        if created_by is not None:
            stmt = stmt.where(AgentActionModel.created_by == created_by)

        # Сортируем по дате создания (новые сначала)
        stmt = stmt.order_by(AgentActionModel.created_at.desc())

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(model) for model in models]

    def _to_domain(self, model: AgentActionModel) -> AgentAction:
        """Преобразовать SQLAlchemy модель в доменную сущность.

        Args:
            model: SQLAlchemy модель AgentActionModel.

        Returns:
            Доменная сущность AgentAction.
        """
        return AgentAction(
            id=model.id,
            type=model.type,
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            created_by=model.created_by,
            data=model.data,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

