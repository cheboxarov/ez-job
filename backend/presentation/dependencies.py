from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, AsyncGenerator, Dict

from fastapi import Depends, HTTPException

from application.factories.database_factory import create_unit_of_work
from application.factories.search_and_generate_cover_letters_factory import (
    create_search_and_generate_cover_letters_usecase,
)
from application.factories.search_and_get_filtered_vacancy_list_factory import (
    create_search_and_get_filtered_vacancy_list_usecase,
)
from application.services.filter_settings_generation_service import (
    FilterSettingsGenerationService,
)
from application.services.vacancies_service import VacanciesService
from application.services.vacancy_responses_service import VacancyResponsesService

if TYPE_CHECKING:
    from application.services.agent_action_service import AgentActionService
from config import AppConfig, load_config
from domain.entities.user import User
from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from domain.use_cases.fetch_chat_detail import FetchChatDetailUseCase
from domain.use_cases.fetch_user_chats import FetchUserChatsUseCase
from domain.use_cases.list_agent_actions import ListAgentActionsUseCase
from domain.use_cases.send_chat_message import SendChatMessageUseCase
from domain.use_cases.generate_user_filter_settings import GenerateUserFilterSettingsUseCase
from domain.use_cases.get_areas import GetAreasUseCase
from infrastructure.auth.fastapi_users_setup import get_current_active_user
from infrastructure.clients.hh_client import RateLimitedHHHttpClient
from infrastructure.database.models.user_model import UserModel
from infrastructure.agents.filter_settings_generator_agent import FilterSettingsGeneratorAgent


@lru_cache()
def get_config() -> AppConfig:
    """Получает конфигурацию приложения (кешируется)."""
    return load_config()


@lru_cache()
def get_vacancies_service() -> VacanciesService:
    """Создает и возвращает VacanciesService (кешируется).

    Returns:
        Инстанс VacanciesService с настроенными зависимостями.
    """
    config = get_config()
    use_case = create_search_and_generate_cover_letters_usecase(config)
    list_use_case = create_search_and_get_filtered_vacancy_list_usecase(config)
    from infrastructure.clients.hh_client import RateLimitedHHHttpClient
    from domain.use_cases.respond_to_vacancy import RespondToVacancyUseCase
    from domain.use_cases.respond_to_vacancy_and_save import RespondToVacancyAndSaveUseCase
    from domain.use_cases.create_vacancy_response import CreateVacancyResponseUseCase
    
    hh_client = RateLimitedHHHttpClient(base_url=config.hh.base_url)
    respond_uc = RespondToVacancyUseCase(hh_client)
    
    # Создаем RespondToVacancyAndSaveUseCase
    # Для этого нужен CreateVacancyResponseUseCase, но он требует UnitOfWork
    # Поэтому создадим его через async функцию или передадим None и создадим в endpoint
    # Пока передадим None, создадим в endpoint
    return VacanciesService(use_case, list_use_case, respond_uc, None)


@lru_cache()
def get_areas_use_case() -> GetAreasUseCase:
    """Создаёт и кеширует GetAreasUseCase с RateLimitedHHHttpClient."""
    config = get_config()
    hh_client = RateLimitedHHHttpClient(base_url=config.hh.base_url)
    return GetAreasUseCase(hh_client)


@lru_cache()
def get_filter_settings_generation_service() -> FilterSettingsGenerationService:
    """Создает сервис генерации предложенных настроек фильтров (кешируется)."""
    config = get_config()
    agent = FilterSettingsGeneratorAgent(config.openai)
    use_case = GenerateUserFilterSettingsUseCase(agent)
    return FilterSettingsGenerationService(use_case)


async def get_unit_of_work() -> AsyncGenerator[UnitOfWorkPort, None]:
    """Dependency для получения UnitOfWork.

    Yields:
        UnitOfWork для управления транзакциями.
    """
    config = get_config()
    unit_of_work = create_unit_of_work(config.database)
    async with unit_of_work:
        yield unit_of_work


async def get_headers(
    current_user: UserModel = Depends(get_current_active_user),
) -> Dict[str, str]:
    """Возвращает заголовки для запросов к HH API из БД пользователя.

    Args:
        current_user: Текущий авторизованный пользователь.

    Returns:
        Словарь headers для HH API.

    Raises:
        HTTPException: 400 если HH auth data не заполнено у пользователя.
    """
    headers = current_user.hh_headers
    if not headers:
        raise HTTPException(
            status_code=400,
            detail="HH auth data not set",
        )
    return headers


# Dependency для получения текущего авторизованного пользователя (модель)
# Используется напрямую из fastapi_users_setup
get_current_user = get_current_active_user


async def get_current_user_domain(
    current_user_model: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> User:
    """Dependency для получения доменной сущности User текущего авторизованного пользователя.

    Args:
        current_user_model: Модель пользователя из FastAPI Users.
        unit_of_work: UnitOfWork для работы с репозиторием.

    Returns:
        Доменная сущность User.

    Raises:
        HTTPException: 404 если пользователь не найден в репозитории.
    """
    user = await unit_of_work.user_repository.get_by_id(current_user_model.id)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"Пользователь с ID {current_user_model.id} не найден"
        )
    return user


async def get_cookies(
    current_user: UserModel = Depends(get_current_active_user),
) -> Dict[str, str]:
    """Возвращает cookies для запросов к HH API из БД пользователя.

    Args:
        current_user: Текущий авторизованный пользователь.

    Returns:
        Словарь cookies для HH API.

    Raises:
        HTTPException: 400 если HH auth data не заполнено у пользователя.
    """
    cookies = current_user.hh_cookies
    if not cookies:
        raise HTTPException(
            status_code=400,
            detail="HH auth data not set",
        )
    return cookies


async def get_vacancy_responses_service(
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> VacancyResponsesService:
    """Создает и возвращает VacancyResponsesService.

    Args:
        unit_of_work: UnitOfWork для работы с репозиториями.

    Returns:
        Инстанс VacancyResponsesService с настроенными зависимостями.
    """
    from domain.use_cases.get_vacancy_responses_by_resume import (
        GetVacancyResponsesByResumeUseCase,
    )

    use_case = GetVacancyResponsesByResumeUseCase(
        resume_repository=unit_of_work.resume_repository,
        vacancy_response_repository=unit_of_work.vacancy_response_repository,
    )
    return VacancyResponsesService(get_vacancy_responses_by_resume_uc=use_case)


@lru_cache()
def get_hh_auth_service():
    """Создает и возвращает HhAuthService.

    Returns:
        Инстанс HhAuthService с настроенными зависимостями.
    """
    from application.services.hh_auth_service import HhAuthService
    from domain.interfaces.hh_auth_service_port import HhAuthServicePort
    from infrastructure.clients.hh_client import HHHttpClient

    config = get_config()
    hh_client = HHHttpClient(base_url=config.hh.base_url)
    service: HhAuthServicePort = HhAuthService(
        hh_client=hh_client,
        login_trust_flags_public_key=config.hh.login_trust_flags_public_key,
    )
    return service


@lru_cache()
def get_fetch_user_chats_uc() -> FetchUserChatsUseCase:
    """Создает и возвращает FetchUserChatsUseCase (кешируется).

    Returns:
        Инстанс FetchUserChatsUseCase с настроенными зависимостями.
    """
    config = get_config()
    hh_client = RateLimitedHHHttpClient(base_url=config.hh.base_url)
    return FetchUserChatsUseCase(hh_client)


@lru_cache()
def get_fetch_chat_detail_uc() -> FetchChatDetailUseCase:
    """Создает и возвращает FetchChatDetailUseCase (кешируется).

    Returns:
        Инстанс FetchChatDetailUseCase с настроенными зависимостями.
    """
    config = get_config()
    hh_client = RateLimitedHHHttpClient(base_url=config.hh.base_url)
    return FetchChatDetailUseCase(hh_client)


@lru_cache()
def get_send_chat_message_uc() -> SendChatMessageUseCase:
    """Создает и возвращает SendChatMessageUseCase (кешируется).

    Returns:
        Инстанс SendChatMessageUseCase с настроенными зависимостями.
    """
    config = get_config()
    hh_client = RateLimitedHHHttpClient(base_url=config.hh.base_url)
    return SendChatMessageUseCase(hh_client)


async def get_list_agent_actions_uc(
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> ListAgentActionsUseCase:
    """Создает и возвращает ListAgentActionsUseCase.

    Args:
        unit_of_work: UnitOfWork для работы с репозиториями.

    Returns:
        Инстанс ListAgentActionsUseCase с настроенными зависимостями.
    """
    return ListAgentActionsUseCase(unit_of_work.agent_action_repository)


async def get_agent_action_service(
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
    send_chat_message_uc: SendChatMessageUseCase = Depends(get_send_chat_message_uc),
) -> AgentActionService:
    """Создает и возвращает AgentActionService.

    Args:
        unit_of_work: UnitOfWork для работы с репозиториями.
        send_chat_message_uc: Use case для отправки сообщений в чат.

    Returns:
        Инстанс AgentActionService с настроенными зависимостями.
    """
    from application.services.agent_action_service import AgentActionService
    from domain.interfaces.agent_action_service_port import AgentActionServicePort

    service: AgentActionServicePort = AgentActionService(
        unit_of_work=unit_of_work,
        send_chat_message_uc=send_chat_message_uc,
    )
    return service

