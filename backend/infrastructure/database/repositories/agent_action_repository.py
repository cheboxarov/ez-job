"""Реализация репозитория действий агента."""

from __future__ import annotations

from typing import List, Union
from uuid import UUID, uuid4

from sqlalchemy import select, update, func, or_
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from domain.entities.agent_action import AgentAction
from domain.interfaces.agent_action_repository_port import AgentActionRepositoryPort
from infrastructure.database.models.agent_action_model import AgentActionModel
from infrastructure.database.repositories.base_repository import BaseRepository


class AgentActionRepository(BaseRepository, AgentActionRepositoryPort):
    """Реализация репозитория действий агента для SQLAlchemy."""

    def __init__(
        self, 
        session_or_factory: Union[AsyncSession, async_sessionmaker[AsyncSession]]
    ) -> None:
        """Инициализация репозитория.

        Args:
            session_or_factory: Либо AsyncSession (для транзакционного режима),
                               либо async_sessionmaker (для standalone режима).
        """
        super().__init__(session_or_factory)

    async def create(self, action: AgentAction) -> AgentAction:
        """Создать действие агента.

        Args:
            action: Доменная сущность AgentAction для создания.
                   Поле id может быть не заполнено (будет сгенерировано).

        Returns:
            Созданная доменная сущность AgentAction с заполненными id, created_at и updated_at.
        """
        async with self._get_session() as session:
            # Генерируем ID, если не указан
            action_id = action.id if action.id else uuid4()

            model = AgentActionModel(
                id=action_id,
                type=action.type,
                entity_type=action.entity_type,
                entity_id=action.entity_id,
                created_by=action.created_by,
                user_id=action.user_id,
                resume_hash=action.resume_hash,
                data=action.data,
                is_read=action.is_read,
            )
            session.add(model)
            await session.flush()
            await session.refresh(model)
            return self._to_domain(model)

    async def list(
        self,
        *,
        types: list[str] | None = None,
        exclude_types: list[str] | None = None,
        event_types: list[str] | None = None,
        exclude_event_types: list[str] | None = None,
        statuses: list[str] | None = None,
        entity_type: str | None = None,
        entity_id: int | None = None,
        created_by: str | None = None,
    ) -> List[AgentAction]:
        """Получить список действий с опциональной фильтрацией.

        Args:
            types: Фильтр по списку типов действий.
            exclude_types: Исключить указанные типы действий.
            event_types: Фильтр по подтипам событий (data["event_type"]) для create_event.
            exclude_event_types: Исключить указанные подтипы событий (data["event_type"]).
            statuses: Фильтр по статусам (data["status"]) для create_event.
            entity_type: Фильтр по типу сущности.
            entity_id: Фильтр по ID сущности.
            created_by: Фильтр по идентификатору агента.

        Returns:
            Список доменных сущностей AgentAction, отсортированный по created_at (desc).
        """
        async with self._get_session() as session:
            stmt = select(AgentActionModel)

            # Динамически добавляем фильтры
            if types:
                stmt = stmt.where(AgentActionModel.type.in_(types))
            if exclude_types:
                stmt = stmt.where(AgentActionModel.type.notin_(exclude_types))
            if entity_type is not None:
                stmt = stmt.where(AgentActionModel.entity_type == entity_type)
            if entity_id is not None:
                stmt = stmt.where(AgentActionModel.entity_id == entity_id)
            if created_by is not None:
                stmt = stmt.where(AgentActionModel.created_by == created_by)
            if event_types:
                has_types = bool(types)
                has_other_types = any(item != "create_event" for item in types or [])
                event_type_condition = AgentActionModel.data["event_type"].astext.in_(event_types)
                if has_types and has_other_types:
                    stmt = stmt.where(
                        or_(
                            AgentActionModel.type != "create_event",
                            event_type_condition,
                        )
                    )
                else:
                    stmt = stmt.where(
                        AgentActionModel.type == "create_event",
                        event_type_condition,
                    )
            if exclude_event_types:
                stmt = stmt.where(
                    or_(
                        AgentActionModel.type != "create_event",
                        AgentActionModel.data["event_type"].astext.notin_(exclude_event_types),
                    )
                )
            if statuses:
                has_types = bool(types)
                has_other_types = any(item != "create_event" for item in types or [])
                status_condition = AgentActionModel.data["status"].astext.in_(statuses)
                if has_types and has_other_types:
                    stmt = stmt.where(
                        or_(
                            AgentActionModel.type != "create_event",
                            status_condition,
                        )
                    )
                else:
                    stmt = stmt.where(
                        AgentActionModel.type == "create_event",
                        status_condition,
                    )

            # Сортируем по дате создания (новые сначала)
            stmt = stmt.order_by(AgentActionModel.created_at.desc())

            result = await session.execute(stmt)
            models = result.scalars().all()

            return [self._to_domain(model) for model in models]

    async def get_unread_count(self, user_id: UUID) -> int:
        async with self._get_session() as session:
            stmt = select(func.count()).select_from(AgentActionModel).where(
                AgentActionModel.user_id == user_id,
                AgentActionModel.is_read.is_(False),
            )
            result = await session.execute(stmt)
            return int(result.scalar_one())

    async def mark_all_as_read(self, user_id: UUID) -> None:
        async with self._get_session() as session:
            stmt = (
                update(AgentActionModel)
                .where(
                    AgentActionModel.user_id == user_id,
                    AgentActionModel.is_read.is_(False),
                )
                .values(is_read=True)
            )
            await session.execute(stmt)

    async def update(self, action: AgentAction) -> AgentAction:
        """Обновить действие агента.

        Args:
            action: Доменная сущность AgentAction с обновленными данными.

        Returns:
            Обновленная доменная сущность AgentAction.

        Raises:
            ValueError: Если действие с таким ID не найдено.
        """
        async with self._get_session() as session:
            stmt = select(AgentActionModel).where(AgentActionModel.id == action.id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                raise ValueError(f"Действие с ID {action.id} не найдено")

            model.type = action.type
            model.entity_type = action.entity_type
            model.entity_id = action.entity_id
            model.created_by = action.created_by
            model.user_id = action.user_id
            model.resume_hash = action.resume_hash
            model.data = action.data
            model.is_read = action.is_read

            await session.flush()
            await session.refresh(model)

            return self._to_domain(model)

    async def get_by_id(self, action_id: UUID) -> AgentAction | None:
        """Получить действие агента по ID.

        Args:
            action_id: UUID действия.

        Returns:
            Доменная сущность AgentAction или None, если не найдено.
        """
        async with self._get_session() as session:
            stmt = select(AgentActionModel).where(AgentActionModel.id == action_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._to_domain(model)

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
            user_id=model.user_id,
            resume_hash=model.resume_hash,
            data=model.data,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_read=model.is_read,
        )
