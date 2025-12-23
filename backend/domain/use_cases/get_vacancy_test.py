"""Use case для получения теста вакансии."""

from __future__ import annotations

from typing import Dict, Optional

from loguru import logger

from domain.entities.vacancy_test import VacancyTest
from domain.interfaces.hh_client_port import HHClientPort


class GetVacancyTestUseCase:
    """Use case для получения теста вакансии из HeadHunter.

    Получает HTML страницу с тестом и парсит её для извлечения вопросов.
    """

    def __init__(
        self,
        hh_client: HHClientPort,
    ) -> None:
        """Инициализация use case.

        Args:
            hh_client: Клиент для работы с HeadHunter API.
        """
        self._hh_client = hh_client

    async def execute(
        self,
        vacancy_id: int,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
    ) -> Optional[VacancyTest]:
        """Получить тест вакансии.

        Args:
            vacancy_id: ID вакансии в HH.
            headers: HTTP заголовки для запроса к HH API.
            cookies: HTTP cookies для запроса к HH API.
            internal_api_base_url: Базовый URL внутреннего API HH.

        Returns:
            VacancyTest если тест найден, None если теста нет или произошла ошибка.
        """
        result = await self._hh_client.get_vacancy_test(
            vacancy_id=vacancy_id,
            headers=headers,
            cookies=cookies,
            internal_api_base_url=internal_api_base_url,
        )
        
        # Если результат - tuple (result, cookies), берем первый элемент
        if isinstance(result, tuple):
            test = result[0]
        else:
            test = result
        
        if test is None:
            logger.info(f"Тест для вакансии {vacancy_id} не найден (форма с тестом отсутствует в HTML)")
            return None
        
        logger.info(
            f"Получен тест для вакансии {vacancy_id}: {len(test.questions)} вопросов"
        )
        return test

