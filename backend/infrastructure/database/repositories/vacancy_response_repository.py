"""Реализация репозитория откликов на вакансии."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from loguru import logger
from sqlalchemy import func, select, cast, Date, distinct, and_
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.vacancy_response import VacancyResponse
from domain.interfaces.vacancy_response_repository_port import (
    VacancyResponseRepositoryPort,
)
from infrastructure.database.models.vacancy_response_model import VacancyResponseModel
from infrastructure.database.models.user_subscription_model import UserSubscriptionModel


class VacancyResponseRepository(VacancyResponseRepositoryPort):
    """Реализация репозитория откликов на вакансии для SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория.

        Args:
            session: Async сессия SQLAlchemy.
        """
        self._session = session

    async def create(self, vacancy_response: VacancyResponse) -> VacancyResponse:
        """Создать отклик на вакансию.

        Args:
            vacancy_response: Доменная сущность VacancyResponse для создания.

        Returns:
            Созданная доменная сущность VacancyResponse с заполненным id.
        """
        logger.info(
            f"Сохранение отклика в БД: vacancy_id={vacancy_response.vacancy_id}, "
            f"resume_id={vacancy_response.resume_id}, resume_hash={vacancy_response.resume_hash}, "
            f"user_id={vacancy_response.user_id}"
        )
        
        if not vacancy_response.resume_hash:
            logger.warning(
                f"ВНИМАНИЕ: resume_hash равен None для vacancy_id={vacancy_response.vacancy_id}, "
                f"resume_id={vacancy_response.resume_id}. Отклик будет сохранен без resume_hash."
            )
        
        model = VacancyResponseModel(
            id=vacancy_response.id,
            vacancy_id=vacancy_response.vacancy_id,
            resume_id=vacancy_response.resume_id,
            resume_hash=vacancy_response.resume_hash,
            user_id=vacancy_response.user_id,
            cover_letter=vacancy_response.cover_letter,
            vacancy_name=vacancy_response.vacancy_name,
            vacancy_url=vacancy_response.vacancy_url,
            created_at=vacancy_response.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        logger.info(
            f"Отклик сохранен в БД (после flush): id={model.id}, "
            f"resume_hash={model.resume_hash!r}, "
            f"resume_hash тип={type(model.resume_hash)}, "
            f"resume_hash длина={len(model.resume_hash) if model.resume_hash else None}, "
            f"vacancy_id={model.vacancy_id}, resume_id={model.resume_id}"
        )
        return self._to_domain(model)

    async def get_by_resume_id_with_pagination(
        self, resume_id: UUID, offset: int, limit: int
    ) -> tuple[list[VacancyResponse], int]:
        """Получить отклики по resume_id с пагинацией.

        Args:
            resume_id: UUID резюме.
            offset: Смещение для пагинации.
            limit: Количество записей для возврата.

        Returns:
            Кортеж из списка откликов и общего количества откликов.
        """
        # Получаем список откликов с пагинацией
        logger.info(
            f"Запрос откликов: resume_id={resume_id}, offset={offset}, limit={limit}"
        )
        stmt = (
            select(VacancyResponseModel)
            .where(VacancyResponseModel.resume_id == resume_id)
            .order_by(VacancyResponseModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        logger.info(f"Найдено моделей в БД: {len(models)}")
        responses = [self._to_domain(model) for model in models]

        # Получаем общее количество откликов
        count_stmt = (
            select(func.count())
            .select_from(VacancyResponseModel)
            .where(VacancyResponseModel.resume_id == resume_id)
        )
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()
        logger.info(f"Общее количество откликов для resume_id={resume_id}: {total}")

        return responses, total

    async def get_by_resume_hash_with_pagination(
        self, resume_hash: str, offset: int, limit: int
    ) -> tuple[list[VacancyResponse], int]:
        """Получить отклики по resume_hash с пагинацией.

        Args:
            resume_hash: Hash резюме.
            offset: Смещение для пагинации.
            limit: Количество записей для возврата.

        Returns:
            Кортеж из списка откликов и общего количества откликов.
        """
        logger.info(
            f"Запрос откликов по hash: resume_hash={resume_hash!r}, "
            f"тип={type(resume_hash)}, длина={len(resume_hash) if resume_hash else None}, "
            f"offset={offset}, limit={limit}"
        )
        
        # Проверяем, есть ли вообще отклики с таким hash (для отладки)
        debug_stmt = (
            select(VacancyResponseModel.resume_hash, func.count())
            .group_by(VacancyResponseModel.resume_hash)
            .limit(10)
        )
        debug_result = await self._session.execute(debug_stmt)
        debug_rows = debug_result.all()
        logger.info(f"Примеры resume_hash в БД: {[(str(h)[:20] if h else None, c) for h, c in debug_rows]}")
        
        stmt = (
            select(VacancyResponseModel)
            .where(VacancyResponseModel.resume_hash == resume_hash)
            .order_by(VacancyResponseModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        logger.info(
            f"Найдено моделей в БД по hash: {len(models)}. "
            f"Примеры найденных resume_hash: {[str(m.resume_hash)[:20] if m.resume_hash else None for m in models[:3]]}"
        )
        responses = [self._to_domain(model) for model in models]

        count_stmt = (
            select(func.count())
            .select_from(VacancyResponseModel)
            .where(VacancyResponseModel.resume_hash == resume_hash)
        )
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()
        logger.info(f"Общее количество откликов для resume_hash={resume_hash!r}: {total}")

        return responses, total

    async def get_responses_count_by_date_range(
        self, user_id: UUID, start_date: date, end_date: date
    ) -> list[tuple[date, int]]:
        """Получить количество откликов по дням за указанный период.
        
        Args:
            user_id: UUID пользователя.
            start_date: Начальная дата (включительно).
            end_date: Конечная дата (включительно).
            
        Returns:
            Список кортежей (дата, количество откликов) для каждого дня в диапазоне.
        """
        logger.info(
            f"Запрос статистики откликов: user_id={user_id}, "
            f"start_date={start_date}, end_date={end_date}"
        )
        
        # Преобразуем даты в datetime для сравнения с created_at (который имеет timezone)
        # Используем UTC timezone для корректного сравнения
        start_datetime = datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc)
        end_datetime = datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc)
        
        # Запрос для группировки по дате и подсчета откликов
        stmt = (
            select(
                cast(VacancyResponseModel.created_at, Date).label("response_date"),
                func.count(VacancyResponseModel.id).label("count")
            )
            .where(
                VacancyResponseModel.user_id == user_id,
                VacancyResponseModel.created_at >= start_datetime,
                VacancyResponseModel.created_at < end_datetime + timedelta(days=1)
            )
            .group_by(cast(VacancyResponseModel.created_at, Date))
            .order_by(cast(VacancyResponseModel.created_at, Date))
        )
        
        result = await self._session.execute(stmt)
        rows = result.all()
        
        # Создаем словарь для быстрого доступа
        data_dict = {row.response_date: row.count for row in rows}
        
        # Заполняем все дни в диапазоне (даже если откликов не было)
        result_list = []
        current_date = start_date
        while current_date <= end_date:
            count = data_dict.get(current_date, 0)
            result_list.append((current_date, count))
            current_date += timedelta(days=1)
        
        logger.info(
            f"Получено {len(result_list)} дней статистики, "
            f"всего откликов: {sum(count for _, count in result_list)}"
        )
        
        return result_list

    async def get_metrics_by_period(
        self,
        *,
        start_date: datetime,
        end_date: datetime,
        plan_id: UUID | None = None,
        time_step: str = "day",
    ) -> list[tuple[datetime, int, int]]:
        """Получить метрики откликов по периоду с группировкой по времени."""
        # Определяем функцию для группировки по времени
        if time_step == "day":
            time_group = func.date_trunc("day", VacancyResponseModel.created_at)
        elif time_step == "week":
            time_group = func.date_trunc("week", VacancyResponseModel.created_at)
        elif time_step == "month":
            time_group = func.date_trunc("month", VacancyResponseModel.created_at)
        else:
            time_group = func.date_trunc("day", VacancyResponseModel.created_at)

        # Базовый запрос
        stmt = (
            select(
                time_group.label("period_start"),
                func.count(VacancyResponseModel.id).label("responses_count"),
                func.count(distinct(VacancyResponseModel.user_id)).label("unique_users"),
            )
            .where(
                and_(
                    VacancyResponseModel.created_at >= start_date,
                    VacancyResponseModel.created_at <= end_date,
                )
            )
            .group_by(time_group)
            .order_by(time_group)
        )

        # Фильтр по плану подписки
        if plan_id:
            stmt = stmt.join(
                UserSubscriptionModel,
                VacancyResponseModel.user_id == UserSubscriptionModel.user_id,
            ).where(UserSubscriptionModel.subscription_plan_id == plan_id)

        result = await self._session.execute(stmt)
        rows = result.all()

        return [
            (
                row.period_start,
                int(row.responses_count),
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
    ) -> tuple[int, int, float]:
        """Получить суммарные метрики откликов за период."""
        stmt = (
            select(
                func.count(VacancyResponseModel.id).label("responses_count"),
                func.count(distinct(VacancyResponseModel.user_id)).label("unique_users"),
            )
            .where(
                and_(
                    VacancyResponseModel.created_at >= start_date,
                    VacancyResponseModel.created_at <= end_date,
                )
            )
        )

        if plan_id:
            stmt = stmt.join(
                UserSubscriptionModel,
                VacancyResponseModel.user_id == UserSubscriptionModel.user_id,
            ).where(UserSubscriptionModel.subscription_plan_id == plan_id)

        result = await self._session.execute(stmt)
        row = result.one()

        responses_count = int(row.responses_count or 0)
        unique_users = int(row.unique_users or 0)
        avg_responses_per_user = responses_count / unique_users if unique_users > 0 else 0.0

        return responses_count, unique_users, avg_responses_per_user

    def _to_domain(self, model: VacancyResponseModel) -> VacancyResponse:
        """Преобразовать SQLAlchemy модель в доменную сущность.

        Args:
            model: SQLAlchemy модель VacancyResponseModel.

        Returns:
            Доменная сущность VacancyResponse.
        """
        return VacancyResponse(
            id=model.id,
            vacancy_id=model.vacancy_id,
            resume_id=model.resume_id,
            resume_hash=model.resume_hash,
            user_id=model.user_id,
            cover_letter=model.cover_letter,
            vacancy_name=model.vacancy_name,
            vacancy_url=model.vacancy_url,
            created_at=model.created_at,
        )
