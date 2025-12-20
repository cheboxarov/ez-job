from __future__ import annotations

from config import AppConfig
from domain.use_cases.generate_cover_letter import GenerateCoverLetterUseCase
from domain.use_cases.search_and_generate_cover_letters import (
    SearchAndGenerateCoverLettersUseCase,
)
from domain.use_cases.search_and_get_filtered_vacancies import (
    SearchAndGetFilteredVacanciesUseCase,
)
from infrastructure.agents.cover_letter_agent import CoverLetterAgent
from infrastructure.agents.vacancy_filter_agent import VacancyFilterAgent
from infrastructure.clients.hh_client import RateLimitedHHHttpClient
from domain.use_cases.fetch_vacancies import FetchVacanciesUseCase
from domain.use_cases.filter_vacancies import FilterVacanciesUseCase
from domain.use_cases.get_filtered_vacancies import GetFilteredVacanciesUseCase


def create_search_and_generate_cover_letters_usecase(
    config: AppConfig,
) -> SearchAndGenerateCoverLettersUseCase:
    """Фабрика для создания SearchAndGenerateCoverLettersUseCase со всеми зависимостями.

    Args:
        config: Конфигурация приложения.

    Returns:
        Инстанс SearchAndGenerateCoverLettersUseCase с настроенными зависимостями.
    """
    # Создаем HH клиент
    hh_client = RateLimitedHHHttpClient(base_url=config.hh.base_url)

    # Создаем FetchVacanciesUseCase
    fetch_vacancies_uc = FetchVacanciesUseCase(
        hh_client,
        max_vacancies=config.hh.max_vacancies,
    )

    # Создаем VacancyFilterAgent
    vacancy_filter_service = VacancyFilterAgent(config.openai)

    # Создаем FilterVacanciesUseCase
    filter_vacancies_uc = FilterVacanciesUseCase(
        filter_service=vacancy_filter_service,
        minimal_confidence=config.openai.minimal_confidence,
        batch_size=50,
    )

    # Создаем GetFilteredVacanciesUseCase
    get_filtered_vacancies_uc = GetFilteredVacanciesUseCase(
        fetch_vacancies_uc=fetch_vacancies_uc,
        filter_vacancies_uc=filter_vacancies_uc,
    )

    # Создаем SearchAndGetFilteredVacanciesUseCase
    search_and_get_filtered_vacancies_uc = SearchAndGetFilteredVacanciesUseCase(
        get_filtered_vacancies_uc=get_filtered_vacancies_uc,
    )

    # Создаем CoverLetterAgent
    cover_letter_agent = CoverLetterAgent(config.openai)

    # Создаем GenerateCoverLetterUseCase
    generate_cover_letter_uc = GenerateCoverLetterUseCase(
        cover_letter_service=cover_letter_agent,
    )

    # Создаем и возвращаем SearchAndGenerateCoverLettersUseCase
    return SearchAndGenerateCoverLettersUseCase(
        search_and_get_filtered_vacancies_uc=search_and_get_filtered_vacancies_uc,
        generate_cover_letter_uc=generate_cover_letter_uc,
    )
