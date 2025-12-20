"""Сервис приложения для управления резюме."""

from __future__ import annotations

from uuid import UUID

from typing import Dict

from domain.entities.resume import Resume
from domain.interfaces.hh_client_port import HHClientPort
from domain.interfaces.resume_service_port import ResumeServicePort
from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from domain.use_cases.create_resume import CreateResumeUseCase
from domain.use_cases.delete_resume import DeleteResumeUseCase
from domain.use_cases.get_resume import GetResumeUseCase
from domain.use_cases.import_resume_from_hh import ImportResumeFromHHUseCase
from domain.use_cases.list_user_resumes import ListUserResumesUseCase
from domain.use_cases.update_resume import UpdateResumeUseCase


class ResumesService(ResumeServicePort):
    """Сервис для управления резюме, оркестрирующий use case'ы."""

    def __init__(self, unit_of_work: UnitOfWorkPort) -> None:
        """Инициализация сервиса.

        Args:
            unit_of_work: UnitOfWork для управления транзакциями.
        """
        self._unit_of_work = unit_of_work

    async def create_resume(
        self,
        user_id: UUID,
        content: str,
        user_parameters: str | None = None,
    ) -> Resume:
        """Создать резюме для пользователя.

        Args:
            user_id: UUID пользователя.
            content: Текст резюме.
            user_parameters: Дополнительные параметры фильтрации.

        Returns:
            Созданная доменная сущность Resume.
        """
        async with self._unit_of_work:
            use_case = CreateResumeUseCase(self._unit_of_work.resume_repository)
            resume = await use_case.execute(
                user_id=user_id,
                content=content,
                user_parameters=user_parameters,
            )
            await self._unit_of_work.commit()
            return resume

    async def get_resume(self, resume_id: UUID, user_id: UUID) -> Resume | None:
        """Получить резюме по ID.

        Проверяет принадлежность резюме пользователю перед возвратом.

        Args:
            resume_id: UUID резюме.
            user_id: UUID пользователя (для проверки принадлежности).

        Returns:
            Доменная сущность Resume или None, если не найдено.

        Raises:
            PermissionError: Если резюме не принадлежит пользователю.
        """
        async with self._unit_of_work:
            use_case = GetResumeUseCase(self._unit_of_work.resume_repository)
            return await use_case.execute(resume_id=resume_id, user_id=user_id)

    async def list_user_resumes(self, user_id: UUID) -> list[Resume]:
        """Получить список резюме пользователя.

        Args:
            user_id: UUID пользователя.

        Returns:
            Список доменных сущностей Resume.
        """
        async with self._unit_of_work:
            use_case = ListUserResumesUseCase(self._unit_of_work.resume_repository)
            return await use_case.execute(user_id=user_id)

    async def update_resume(
        self,
        resume_id: UUID,
        user_id: UUID,
        content: str | None = None,
        user_parameters: str | None = None,
        is_auto_reply: bool | None = None,
    ) -> Resume:
        """Обновить резюме.

        Проверяет принадлежность резюме пользователю перед обновлением.

        Args:
            resume_id: UUID резюме.
            user_id: UUID пользователя (для проверки принадлежности).
            content: Новый текст резюме (опционально).
            user_parameters: Новые параметры фильтрации (опционально).
            is_auto_reply: Включен ли автоматический отклик (опционально).

        Returns:
            Обновленная доменная сущность Resume.

        Raises:
            PermissionError: Если резюме не принадлежит пользователю.
            ValueError: Если резюме не найдено.
        """
        async with self._unit_of_work:
            use_case = UpdateResumeUseCase(self._unit_of_work.resume_repository)
            resume = await use_case.execute(
                resume_id=resume_id,
                user_id=user_id,
                content=content,
                user_parameters=user_parameters,
                is_auto_reply=is_auto_reply,
            )
            await self._unit_of_work.commit()
            return resume

    async def delete_resume(self, resume_id: UUID, user_id: UUID) -> None:
        """Удалить резюме.

        Проверяет принадлежность резюме пользователю перед удалением.

        Args:
            resume_id: UUID резюме.
            user_id: UUID пользователя (для проверки принадлежности).

        Raises:
            PermissionError: Если резюме не принадлежит пользователю.
            ValueError: Если резюме не найдено.
        """
        async with self._unit_of_work:
            use_case = DeleteResumeUseCase(self._unit_of_work.resume_repository)
            await use_case.execute(resume_id=resume_id, user_id=user_id)
            await self._unit_of_work.commit()

    async def import_resume_from_hh(
        self,
        user_id: UUID,
        hh_client: HHClientPort,
        headers: Dict[str, str],
        cookies: Dict[str, str],
    ) -> list[Resume]:
        """Импортировать резюме из HeadHunter.

        Args:
            user_id: UUID пользователя.
            hh_client: Клиент для работы с HeadHunter API.
            headers: Заголовки для запроса к HH API.
            cookies: Куки для запроса к HH API.

        Returns:
            Список созданных резюме в БД.
        """
        async with self._unit_of_work:
            use_case = ImportResumeFromHHUseCase(
                hh_client=hh_client,
                resume_repository=self._unit_of_work.resume_repository,
                user_hh_auth_data_repository=self._unit_of_work.user_hh_auth_data_repository,
            )
            resumes = await use_case.execute(
                user_id=user_id,
                headers=headers,
                cookies=cookies,
            )
            await self._unit_of_work.commit()
            return resumes
