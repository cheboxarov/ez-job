"""Реализация репозитория резюме."""

from __future__ import annotations

from loguru import logger
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.resume import Resume
from domain.interfaces.resume_repository_port import ResumeRepositoryPort
from infrastructure.database.models.resume_model import ResumeModel



class ResumeRepository(ResumeRepositoryPort):
    """Реализация репозитория резюме для SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория.

        Args:
            session: Async сессия SQLAlchemy.
        """
        self._session = session

    async def create(self, resume: Resume) -> Resume:
        """Создать резюме.

        Args:
            resume: Доменная сущность Resume для создания.

        Returns:
            Созданная доменная сущность Resume с заполненным id.
        """
        model = ResumeModel(
            id=resume.id,
            user_id=resume.user_id,
            content=resume.content,
            user_parameters=resume.user_parameters,
            external_id=resume.external_id,
            headhunter_hash=resume.headhunter_hash,
            is_auto_reply=resume.is_auto_reply,
            autolike_threshold=resume.autolike_threshold,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def update(self, resume: Resume) -> Resume:
        """Обновить резюме.

        Args:
            resume: Доменная сущность Resume с обновленными данными.

        Returns:
            Обновленная доменная сущность Resume.

        Raises:
            ValueError: Если резюме с таким ID не найдено.
        """
        stmt = select(ResumeModel).where(ResumeModel.id == resume.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            raise ValueError(f"Резюме с ID {resume.id} не найдено")

        model.content = resume.content
        model.user_parameters = resume.user_parameters
        model.headhunter_hash = resume.headhunter_hash
        model.is_auto_reply = resume.is_auto_reply
        model.autolike_threshold = resume.autolike_threshold
        # external_id не обновляем через API (store_only)

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_domain(model)

    async def delete(self, resume_id: UUID) -> None:
        """Удалить резюме.

        Args:
            resume_id: UUID резюме для удаления.

        Raises:
            ValueError: Если резюме с таким ID не найдено.
        """
        stmt = select(ResumeModel).where(ResumeModel.id == resume_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            raise ValueError(f"Резюме с ID {resume_id} не найдено")

        await self._session.delete(model)
        await self._session.flush()

    async def get_by_id(self, resume_id: UUID) -> Resume | None:
        """Получить резюме по ID.

        Args:
            resume_id: UUID резюме.

        Returns:
            Доменная сущность Resume или None, если резюме не найдено.
        """
        stmt = select(ResumeModel).where(ResumeModel.id == resume_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def list_by_user_id(self, user_id: UUID) -> list[Resume]:
        """Получить список резюме по ID пользователя.

        Args:
            user_id: UUID пользователя.

        Returns:
            Список доменных сущностей Resume.
        """
        stmt = select(ResumeModel).where(ResumeModel.user_id == user_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(model) for model in models]

    async def belongs_to_user(self, resume_id: UUID, user_id: UUID) -> bool:
        """Проверить, принадлежит ли резюме пользователю.

        Args:
            resume_id: UUID резюме.
            user_id: UUID пользователя.

        Returns:
            True, если резюме принадлежит пользователю, иначе False.
        """
        stmt = (
            select(ResumeModel.id)
            .where(ResumeModel.id == resume_id)
            .where(ResumeModel.user_id == user_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_by_external_id(
        self, external_id: str, user_id: UUID
    ) -> Resume | None:
        """Получить резюме по external_id и user_id.

        Args:
            external_id: Внешний ID резюме (например, ID из HH).
            user_id: UUID пользователя.

        Returns:
            Доменная сущность Resume или None, если резюме не найдено.
        """
        stmt = (
            select(ResumeModel)
            .where(ResumeModel.external_id == external_id)
            .where(ResumeModel.user_id == user_id)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def get_all_active_auto_reply_resumes(self) -> list[Resume]:
        """Получить все резюме с включенным автооткликом.

        Returns:
            Список доменных сущностей Resume с is_auto_reply = True.
        """
        stmt = select(ResumeModel).where(ResumeModel.is_auto_reply == True)
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(model) for model in models]

    async def get_by_headhunter_hash(
        self, user_id: UUID, headhunter_hash: str
    ) -> Resume | None:
        """Получить резюме по headhunter_hash и user_id.

        Args:
            user_id: UUID пользователя.
            headhunter_hash: Hash резюме в HeadHunter.

        Returns:
            Доменная сущность Resume или None, если резюме не найдено.
        """
        logger.info(
            f"Поиск резюме: headhunter_hash={headhunter_hash}, user_id={user_id}"
        )
        stmt = (
            select(ResumeModel)
            .where(ResumeModel.headhunter_hash == headhunter_hash)
            .where(ResumeModel.user_id == user_id)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            logger.warning(
                f"Резюме не найдено: headhunter_hash={headhunter_hash}, user_id={user_id}"
            )
            # Проверяем, есть ли резюме с таким hash у других пользователей
            stmt_all = select(ResumeModel).where(
                ResumeModel.headhunter_hash == headhunter_hash
            )
            result_all = await self._session.execute(stmt_all)
            models_all = result_all.scalars().all()
            if models_all:
                logger.warning(
                    f"Найдено {len(models_all)} резюме с таким headhunter_hash, "
                    f"но они принадлежат другим пользователям"
                )
            return None

        logger.info(
            f"Найдено резюме: id={model.id}, headhunter_hash={model.headhunter_hash}, user_id={model.user_id}"
        )
        return self._to_domain(model)

    def _to_domain(self, model: ResumeModel) -> Resume:
        """Преобразовать SQLAlchemy модель в доменную сущность.

        Args:
            model: SQLAlchemy модель ResumeModel.

        Returns:
            Доменная сущность Resume.
        """
        return Resume(
            id=model.id,
            user_id=model.user_id,
            content=model.content,
            user_parameters=model.user_parameters,
            external_id=model.external_id,
            headhunter_hash=model.headhunter_hash,
            is_auto_reply=model.is_auto_reply,
            autolike_threshold=model.autolike_threshold,
        )
