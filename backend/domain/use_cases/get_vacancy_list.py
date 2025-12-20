from __future__ import annotations

from typing import Dict, Optional
from uuid import UUID

from domain.entities.resume_filter_settings import ResumeFilterSettings
from domain.entities.vacancy_list import VacancyList
from domain.interfaces.hh_client_port import HHClientPort
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase
from infrastructure.clients.hh_client_with_cookie_update import HHHttpClientWithCookieUpdate


class GetVacancyListUseCase:
    """Use case получения списка вакансий без детальных запросов.

    Получает список вакансий через внутренний API /search/vacancy и возвращает
    краткую информацию без дополнительных запросов к /vacancies/{id}.
    """

    def __init__(
        self,
        hh_client: HHClientPort,
        max_vacancies: int = 50,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
    ) -> None:
        self._hh_client = hh_client
        self._max_vacancies = max_vacancies
        self._internal_api_base_url = internal_api_base_url

    async def execute(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        settings: ResumeFilterSettings,
        text: str,
        page: str,
        search_session_id: str,
        resume_hash: str | None = None,
        order_by: str | None = None,
        user_id: Optional[UUID] = None,
        update_cookies_uc: Optional[UpdateUserHhAuthCookiesUseCase] = None,
    ) -> VacancyList:
        # Собираем query для внутреннего API /search/vacancy
        # Нумерация страниц во внутреннем API обычно с 1, но проверяем
        query: Dict[str, str] = {
            "text": text,
            "page": page,
            "items_on_page": str(self._max_vacancies),
            "enable_snippets": "true",  # Включаем сниппеты для получения описания вакансий
        }

        # Добавляем resume hash для персонализации выдачи
        if resume_hash:
            query["resume"] = resume_hash

        # Добавляем searchSessionId
        query["searchSessionId"] = search_session_id

        # Регион и зарплата
        if settings.area:
            query["area"] = settings.area
        if settings.salary is not None:
            query["salary"] = str(settings.salary)
        if settings.currency:
            query["currency_code"] = settings.currency
        if settings.only_with_salary:
            query["only_with_salary"] = "true"

        # Мультизнаковые фильтры (кома‑разделённый список или массивы в зависимости от API)
        if settings.experience:
            query["experience"] = ",".join(settings.experience)
        if settings.employment:
            query["employment"] = ",".join(settings.employment)
        if settings.schedule:
            query["schedule"] = ",".join(settings.schedule)
        if settings.professional_role:
            query["professional_role"] = ",".join(settings.professional_role)

        # Временные ограничения
        if settings.period is not None:
            query["search_period"] = str(settings.period)
        else:
            if settings.date_from:
                query["date_from"] = settings.date_from
            if settings.date_to:
                query["date_to"] = settings.date_to

        # Сортировка: приоритет явного параметра, затем из настроек
        final_order_by = order_by or settings.order_by
        if final_order_by:
            query["order_by"] = final_order_by

        # Если передан user_id и update_cookies_uc, используем обертку для автоматического сохранения cookies
        if user_id and update_cookies_uc:
            client = HHHttpClientWithCookieUpdate(self._hh_client, user_id, update_cookies_uc)
        else:
            client = self._hh_client
        
        # Используем внутренний API /search/vacancy
        vacancy_list = await client.fetch_vacancy_list_front(
            headers, cookies, query, internal_api_base_url=self._internal_api_base_url
        )
        
        return vacancy_list
