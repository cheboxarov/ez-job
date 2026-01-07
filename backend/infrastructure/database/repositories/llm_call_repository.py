"""Реализация репозитория для логирования вызовов LLM."""

from __future__ import annotations

from typing import Union
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import func, select, and_, or_, case, distinct
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from domain.entities.llm_call import LlmCall
from domain.interfaces.llm_call_repository_port import LlmCallRepositoryPort
from infrastructure.database.models.llm_call_model import LlmCallModel
from infrastructure.database.models.user_subscription_model import UserSubscriptionModel
from infrastructure.database.repositories.base_repository import BaseRepository


class LlmCallRepository(BaseRepository, LlmCallRepositoryPort):
    """Реализация репозитория для логирования вызовов LLM для SQLAlchemy."""

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

    async def create(self, llm_call: LlmCall) -> LlmCall:
        """Создать запись о вызове LLM.

        Args:
            llm_call: Доменная сущность LlmCall для создания.
                     Поле id может быть не заполнено (будет сгенерировано).

        Returns:
            Созданная доменная сущность LlmCall с заполненными id и created_at.
        """
        async with self._get_session() as session:
            # Генерируем ID, если не указан
            llm_call_id = llm_call.id if llm_call.id else uuid4()

            model = LlmCallModel(
                id=llm_call_id,
                call_id=llm_call.call_id,
                attempt_number=llm_call.attempt_number,
                agent_name=llm_call.agent_name,
                model=llm_call.model,
                user_id=llm_call.user_id,
                prompt=llm_call.prompt,
                response=llm_call.response,
                temperature=llm_call.temperature,
                response_format=llm_call.response_format,
                status=llm_call.status,
                error_type=llm_call.error_type,
                error_message=llm_call.error_message,
                duration_ms=llm_call.duration_ms,
                prompt_tokens=llm_call.prompt_tokens,
                completion_tokens=llm_call.completion_tokens,
                total_tokens=llm_call.total_tokens,
                response_size_bytes=llm_call.response_size_bytes,
                cost_usd=llm_call.cost_usd,
                context=llm_call.context,
            )
            session.add(model)
            await session.flush()
            await session.refresh(model)
            return self._to_domain(model)

    async def get_by_id(self, call_id: UUID) -> LlmCall | None:
        """Получить запись о вызове LLM по ID."""
        async with self._get_session() as session:
            stmt = select(LlmCallModel).where(LlmCallModel.id == call_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                return None
            return self._to_domain(model)

    async def list_for_admin(
        self,
        *,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        user_id: UUID | None = None,
        agent_name: str | None = None,
        status: str | None = None,
        page: int,
        page_size: int,
    ) -> tuple[list[LlmCall], int]:
        """Получить список вызовов LLM для админки с фильтрами и пагинацией."""
        async with self._get_session() as session:
            stmt = select(LlmCallModel)

            conditions = []
            if start_date:
                conditions.append(LlmCallModel.created_at >= start_date)
            if end_date:
                conditions.append(LlmCallModel.created_at <= end_date)
            if user_id:
                conditions.append(LlmCallModel.user_id == user_id)
            if agent_name:
                conditions.append(LlmCallModel.agent_name == agent_name)
            if status:
                conditions.append(LlmCallModel.status == status)

            if conditions:
                stmt = stmt.where(and_(*conditions))

            # Подсчет общего количества
            count_stmt = stmt.with_only_columns(func.count()).order_by(None)
            total_result = await session.execute(count_stmt)
            total = int(total_result.scalar_one() or 0)

            # Пагинация
            offset = max(page - 1, 0) * page_size
            stmt = stmt.order_by(LlmCallModel.created_at.desc()).offset(offset).limit(page_size)

            result = await session.execute(stmt)
            models = result.scalars().all()

            return [self._to_domain(model) for model in models], total

    async def get_metrics_by_period(
        self,
        *,
        start_date: datetime,
        end_date: datetime,
        plan_id: UUID | None = None,
        time_step: str = "day",
    ) -> list[tuple[datetime, int, int, int]]:
        """Получить метрики LLM по периоду с группировкой по времени."""
        async with self._get_session() as session:
            # Определяем функцию для группировки по времени
            if time_step == "day":
                time_group = func.date_trunc("day", LlmCallModel.created_at)
            elif time_step == "week":
                time_group = func.date_trunc("week", LlmCallModel.created_at)
            elif time_step == "month":
                time_group = func.date_trunc("month", LlmCallModel.created_at)
            else:
                time_group = func.date_trunc("day", LlmCallModel.created_at)

            # Базовый запрос
            stmt = (
                select(
                    time_group.label("period_start"),
                    func.count(LlmCallModel.id).label("calls_count"),
                    func.coalesce(func.sum(LlmCallModel.total_tokens), 0).label("total_tokens"),
                    func.count(distinct(LlmCallModel.user_id)).label("unique_users"),
                )
                .where(
                    and_(
                        LlmCallModel.created_at >= start_date,
                        LlmCallModel.created_at <= end_date,
                    )
                )
                .group_by(time_group)
                .order_by(time_group)
            )

            # Фильтр по плану подписки
            if plan_id:
                stmt = stmt.join(
                    UserSubscriptionModel,
                    LlmCallModel.user_id == UserSubscriptionModel.user_id,
                ).where(UserSubscriptionModel.subscription_plan_id == plan_id)

            result = await session.execute(stmt)
            rows = result.all()

            return [
                (
                    row.period_start,
                    int(row.calls_count),
                    int(row.total_tokens or 0),
                    int(row.unique_users),
                )
                for row in rows
            ]

    async def get_total_metrics(
        self,
        *,
        start_date: datetime,
        end_date: datetime,
        plan_id: UUID | None = None,
    ) -> tuple[int, int, int, float]:
        """Получить суммарные метрики LLM за период."""
        async with self._get_session() as session:
            stmt = (
                select(
                    func.count(LlmCallModel.id).label("calls_count"),
                    func.coalesce(func.sum(LlmCallModel.total_tokens), 0).label("total_tokens"),
                    func.count(distinct(LlmCallModel.user_id)).label("unique_users"),
                )
                .where(
                    and_(
                        LlmCallModel.created_at >= start_date,
                        LlmCallModel.created_at <= end_date,
                    )
                )
            )

            if plan_id:
                stmt = stmt.join(
                    UserSubscriptionModel,
                    LlmCallModel.user_id == UserSubscriptionModel.user_id,
                ).where(UserSubscriptionModel.subscription_plan_id == plan_id)

            result = await session.execute(stmt)
            row = result.one()

            calls_count = int(row.calls_count or 0)
            total_tokens = int(row.total_tokens or 0)
            unique_users = int(row.unique_users or 0)
            avg_tokens_per_user = total_tokens / unique_users if unique_users > 0 else 0.0

            return calls_count, total_tokens, unique_users, avg_tokens_per_user

    def _to_domain(self, model: LlmCallModel) -> LlmCall:
        """Преобразовать SQLAlchemy модель в доменную сущность.

        Args:
            model: SQLAlchemy модель LlmCallModel.

        Returns:
            Доменная сущность LlmCall.
        """
        return LlmCall(
            id=model.id,
            call_id=model.call_id,
            attempt_number=model.attempt_number,
            agent_name=model.agent_name,
            model=model.model,
            user_id=model.user_id,
            prompt=model.prompt,
            response=model.response,
            temperature=model.temperature,
            response_format=model.response_format,
            status=model.status,
            error_type=model.error_type,
            error_message=model.error_message,
            duration_ms=model.duration_ms,
            prompt_tokens=model.prompt_tokens,
            completion_tokens=model.completion_tokens,
            total_tokens=model.total_tokens,
            response_size_bytes=model.response_size_bytes,
            cost_usd=model.cost_usd,
            context=model.context,
            created_at=model.created_at,
        )
