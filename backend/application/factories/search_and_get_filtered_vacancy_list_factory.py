from __future__ import annotations

from config import AppConfig, DatabaseConfig
from domain.use_cases.get_filtered_vacancy_list import GetFilteredVacancyListUseCase
from domain.use_cases.get_filtered_vacancy_list_with_cache import (
    GetFilteredVacancyListWithCacheUseCase,
)
from domain.use_cases.get_vacancy_list import GetVacancyListUseCase
from domain.use_cases.search_and_get_filtered_vacancy_list import (
    SearchAndGetFilteredVacancyListUseCase,
)
from infrastructure.agents.vacancy_list_filter_agent import VacancyListFilterAgent
from infrastructure.clients.hh_client import RateLimitedHHHttpClient
from infrastructure.database.session import create_session_factory


def create_search_and_get_filtered_vacancy_list_usecase(
    config: AppConfig,
) -> SearchAndGetFilteredVacancyListUseCase:
    """Фабрика для создания SearchAndGetFilteredVacancyListUseCase со всеми зависимостями.

    Args:
        config: Конфигурация приложения.

    Returns:
        Инстанс SearchAndGetFilteredVacancyListUseCase с настроенными зависимостями.
    """
    # Создаем HH клиент
    hh_client = RateLimitedHHHttpClient(base_url=config.hh.base_url)

    # Создаем GetVacancyListUseCase
    internal_api_base_url = getattr(config.hh, "internal_api_base_url", None) or "https://krasnoyarsk.hh.ru"
    get_vacancy_list_uc = GetVacancyListUseCase(
        hh_client,
        max_vacancies=config.hh.max_vacancies,
        internal_api_base_url=internal_api_base_url,
    )

    # Создаем VacancyListFilterAgent
    vacancy_list_filter_service = VacancyListFilterAgent(config.openai)

    # Создаем session_factory для работы с репозиторием мэтчей
    session_factory = create_session_factory(config.database)

    # Создаем GetFilteredVacancyListWithCacheUseCase
    filter_vacancy_list_with_cache_uc = GetFilteredVacancyListWithCacheUseCase(
        session_factory=session_factory,
        filter_service=vacancy_list_filter_service,
        minimal_confidence=config.openai.minimal_confidence,
        batch_size=50,
    )

    # Создаем GetFilteredVacancyListUseCase
    get_filtered_vacancy_list_uc = GetFilteredVacancyListUseCase(
        get_vacancy_list_uc=get_vacancy_list_uc,
        filter_vacancy_list_with_cache_uc=filter_vacancy_list_with_cache_uc,
    )

    # Создаем и возвращаем SearchAndGetFilteredVacancyListUseCase
    return SearchAndGetFilteredVacancyListUseCase(
        get_filtered_vacancy_list_uc=get_filtered_vacancy_list_uc,
    )

