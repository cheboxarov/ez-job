"""Use case для импорта резюме из HeadHunter."""

from __future__ import annotations

from typing import Dict, List
from uuid import UUID, uuid4

from loguru import logger

from domain.entities.hh_resume import HHResume
from domain.entities.resume import Resume
from domain.interfaces.hh_client_port import HHClientPort
from domain.interfaces.resume_repository_port import ResumeRepositoryPort
from domain.interfaces.user_hh_auth_data_repository_port import UserHhAuthDataRepositoryPort
from domain.use_cases.fetch_hh_resume_detail import FetchHHResumeDetailUseCase
from domain.use_cases.fetch_hh_resumes import FetchHHResumesUseCase
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase
from domain.utils.resume_content_formatter import format_hh_resume_to_content


class ImportResumeFromHHUseCase:
    """Use case для импорта резюме из HeadHunter в БД.

    Получает список резюме из HH, для каждого получает детальную информацию,
    формирует текстовый контент и создает резюме в БД.
    """

    def __init__(
        self,
        hh_client: HHClientPort,
        resume_repository: ResumeRepositoryPort,
        user_hh_auth_data_repository: UserHhAuthDataRepositoryPort | None = None,
    ) -> None:
        """Инициализация use case.

        Args:
            hh_client: Клиент для работы с HeadHunter API.
            resume_repository: Репозиторий резюме.
            user_hh_auth_data_repository: Репозиторий для обновления cookies (опционально).
        """
        self._hh_client = hh_client
        self._resume_repository = resume_repository
        self._user_hh_auth_data_repository = user_hh_auth_data_repository

    async def execute(
        self,
        *,
        user_id: UUID,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
    ) -> List[Resume]:
        """Импортировать резюме из HeadHunter.

        Args:
            user_id: UUID пользователя.
            headers: Заголовки для запроса к HH API.
            cookies: Куки для запроса к HH API.
            internal_api_base_url: Базовый URL внутреннего API HH.

        Returns:
            Список созданных резюме в БД.
        """
        # Создаем use case для обновления cookies, если репозиторий доступен
        update_cookies_uc = None
        if self._user_hh_auth_data_repository:
            update_cookies_uc = UpdateUserHhAuthCookiesUseCase(
                self._user_hh_auth_data_repository
            )

        # Получаем список резюме из HH
        fetch_resumes_uc = FetchHHResumesUseCase(self._hh_client)
        hh_resumes = await fetch_resumes_uc.execute(
            headers=headers,
            cookies=cookies,
            internal_api_base_url=internal_api_base_url,
            user_id=user_id,
            update_cookies_uc=update_cookies_uc,
        )

        # Получаем детальную информацию для каждого резюме и создаем в БД
        fetch_detail_uc = FetchHHResumeDetailUseCase(self._hh_client)
        created_resumes: list[Resume] = []

        for hh_resume in hh_resumes:
            try:
                # Получаем детальную информацию
                hh_resume_detail = await fetch_detail_uc.execute(
                    resume_hash=hh_resume.hash,
                    headers=headers,
                    cookies=cookies,
                    internal_api_base_url=internal_api_base_url,
                    user_id=user_id,
                    update_cookies_uc=update_cookies_uc,
                )

                if hh_resume_detail is None:
                    logger.warning(
                        f"Не удалось получить детальную информацию для резюме hash={hh_resume.hash}"
                    )
                    continue

                # Формируем текстовый контент
                content = format_hh_resume_to_content(hh_resume_detail)

                # Проверяем, есть ли резюме с таким external_id в БД
                existing_resume = await self._resume_repository.get_by_external_id(
                    external_id=hh_resume_detail.resume_id,
                    user_id=user_id,
                )

                if existing_resume is not None:
                    # Обновляем существующее резюме
                    existing_resume.content = content
                    existing_resume.headhunter_hash = hh_resume_detail.hash
                    updated_resume = await self._resume_repository.update(existing_resume)
                    created_resumes.append(updated_resume)
                    logger.info(
                        f"Обновлено существующее резюме external_id={hh_resume_detail.resume_id}, "
                        f"id={updated_resume.id}"
                    )
                else:
                    # Создаем новое резюме в БД
                    resume = Resume(
                        id=uuid4(),
                        user_id=user_id,
                        content=content,
                        user_parameters=None,
                        external_id=hh_resume_detail.resume_id,
                        headhunter_hash=hh_resume_detail.hash,
                    )

                    created_resume = await self._resume_repository.create(resume)
                    created_resumes.append(created_resume)
                    logger.info(
                        f"Создано новое резюме external_id={hh_resume_detail.resume_id}, "
                        f"id={created_resume.id}"
                    )

            except Exception as exc:
                logger.error(
                    f"Ошибка при импорте резюме hash={hh_resume.hash}: {exc}",
                    exc_info=True,
                )
                continue

        return created_resumes

