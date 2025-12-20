from __future__ import annotations

import asyncio
from typing import Dict, List, Optional
from uuid import UUID

from domain.entities.resume_filter_settings import ResumeFilterSettings
from domain.entities.vacancy_detail import VacancyDetail
from domain.interfaces.hh_client_port import HHClientPort
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase
from infrastructure.clients.hh_client_with_cookie_update import HHHttpClientWithCookieUpdate


class FetchVacanciesUseCase:
    """Use case получения детализированных вакансий.

    Берёт список вакансий по публичному API /vacancies и для первых N (по умолчанию 50)
    загружает детальные карточки /vacancies/{id} параллельно.
    """

    def __init__(self, hh_client: HHClientPort, max_vacancies: int = 50) -> None:
        self._hh_client = hh_client
        self._max_vacancies = max_vacancies

    async def execute(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        settings: ResumeFilterSettings,
        text: str,
        page: str,
        search_session_id: str,
        order_by: str | None = None,
        user_id: Optional[UUID] = None,
        update_cookies_uc: Optional[UpdateUserHhAuthCookiesUseCase] = None,
    ) -> List[VacancyDetail]:
        # Если передан user_id и update_cookies_uc, используем обертку для автоматического сохранения cookies
        if user_id and update_cookies_uc:
            client = HHHttpClientWithCookieUpdate(self._hh_client, user_id, update_cookies_uc)
        else:
            client = self._hh_client

        # Собираем query из явных аргументов.
        # Для публичного API используем только поддерживаемые фильтры.
        query: Dict[str, str] = {
            "text": text,
            "page": page,
            "per_page": str(self._max_vacancies),
        }

        # Регион и зарплата
        if settings.area:
            query["area"] = settings.area
        if settings.salary is not None:
            query["salary"] = str(settings.salary)
        if settings.currency:
            query["currency"] = settings.currency
        if settings.only_with_salary:
            query["only_with_salary"] = "true"

        # Мультизнаковые фильтры (кома‑разделённый список)
        if settings.experience:
            query["experience"] = ",".join(settings.experience)
        if settings.employment:
            query["employment"] = ",".join(settings.employment)
        if settings.schedule:
            query["schedule"] = ",".join(settings.schedule)
        if settings.professional_role:
            query["professional_role"] = ",".join(settings.professional_role)

        # Временные ограничения: либо period, либо date_from/date_to
        if settings.period is not None:
            query["period"] = str(settings.period)
        else:
            if settings.date_from:
                query["date_from"] = settings.date_from
            if settings.date_to:
                query["date_to"] = settings.date_to

        # Сортировка: приоритет явного параметра, затем из настроек
        final_order_by = order_by or settings.order_by
        if final_order_by:
            query["order_by"] = final_order_by

        vacancy_list = await client.fetch_vacancy_list(headers, cookies, query)
        items = vacancy_list.items[: self._max_vacancies]

        async def _fetch_one(vacancy_id: int) -> VacancyDetail | None:
            return await client.fetch_vacancy_detail(vacancy_id, headers, cookies)

        tasks = [
            asyncio.create_task(_fetch_one(item.vacancy_id))
            for item in items
        ]

        results = await asyncio.gather(*tasks)
        return [detail for detail in results if detail is not None]
