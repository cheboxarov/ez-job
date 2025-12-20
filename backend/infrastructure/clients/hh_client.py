from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Dict, List, Optional, Union

import httpx

from domain.entities.hh_chat_detailed import HHChatDetailed, HHChatMessages
from domain.entities.hh_chat_message import (
    HHChatMessage,
    HHParticipantDisplay,
    HHWorkflowTransition,
)
from domain.entities.hh_list_chat import (
    HHChatDisplayInfo,
    HHChatListItem,
    HHChatOperations,
    HHListChat,
    HHWritePossibility,
)
from domain.entities.hh_resume import HHResume
from domain.entities.hh_resume_detailed import HHResumeDetailed, HHWorkExperience
from domain.entities.vacancy_detail import VacancyDetail
from domain.entities.vacancy_list import VacancyList, VacancyListItem
from domain.interfaces.hh_client_port import HHClientPort


class HHHttpClient(HHClientPort):
    """HTTP‑клиент HH для публичного API (https://api.hh.ru)."""

    def __init__(self, base_url: str = "https://api.hh.ru", timeout: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    @staticmethod
    def _extract_cookies(client: httpx.AsyncClient) -> Dict[str, str]:
        """Безопасно извлекает cookies из httpx клиента.
        
        Обрабатывает случаи, когда есть несколько cookies с одинаковым именем,
        беря последнее значение для каждого имени.
        
        Args:
            client: httpx AsyncClient после выполнения запроса.
            
        Returns:
            Словарь cookies (имя -> значение).
        """
        updated_cookies: Dict[str, str] = {}
        # Итерируемся по всем cookies в jar и берем последнее значение для каждого имени
        for cookie in client.cookies.jar:
            updated_cookies[cookie.name] = cookie.value
        return updated_cookies

    async def fetch_vacancy_list(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        query: Dict[str, str],
        *,
        return_cookies: bool = False,
    ) -> VacancyList | tuple[VacancyList, Dict[str, str]]:
        # Публичное API: GET /vacancies
        url = f"{self._base_url}/vacancies"
        # url = "https://krasnoyarsk.hh.ru/search/vacancy"

        print(f"[list] GET {url} params={query}", flush=True)

        async with httpx.AsyncClient(headers=headers, cookies=cookies, timeout=self._timeout) as client:
            try:
                resp = await client.get(url, params=query)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                print(
                    f"[list] HTTP {response.status_code} for {response.request.url}",
                    flush=True,
                )
                ct = response.headers.get("Content-Type", "")
                print(f"[list] Content-Type: {ct}", flush=True)
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                print(f"[list] Body preview: {body_preview}", flush=True)
                raise

            try:
                payload = resp.json()
            except json.JSONDecodeError as exc:  # pragma: no cover - диагностика
                text = resp.text
                print(
                    f"[list] Не удалось распарсить JSON списка вакансий: {exc}; body_len={len(text)}",
                    flush=True,
                )
                raise RuntimeError(
                    f"Не удалось распарсить JSON списка вакансий: {exc}; body_len={len(text)}"
                ) from exc

            # Извлечь обновленные cookies после запроса
            updated_cookies = self._extract_cookies(client)

        # Структура публичного API: корень -> items: [ { id, name, area, published_at, ... } ]
        raw_vacancies = payload.get("items") or []

        items: list[VacancyListItem] = []
        for raw in raw_vacancies:
            if not isinstance(raw, dict):
                continue

            raw_id = raw.get("id")
            try:
                vacancy_id = int(raw_id)  # id в публичном API — строка, приводим к int
            except (TypeError, ValueError):
                continue

            name = raw.get("name") or ""

            area_name = None
            area = raw.get("area")
            if isinstance(area, dict):
                area_name = area.get("name") or None

            publication_time_iso = None
            published_at = raw.get("published_at")
            if isinstance(published_at, str):
                publication_time_iso = published_at

            # Дополнительные поля
            alternate_url = raw.get("alternate_url") or None

            company_name = None
            employer = raw.get("employer")
            if isinstance(employer, dict):
                company_name = employer.get("name") or None

            salary_from = None
            salary_to = None
            salary_currency = None
            salary_gross = None
            salary = raw.get("salary")
            if isinstance(salary, dict):
                salary_from = salary.get("from")
                salary_to = salary.get("to")
                salary_currency = salary.get("currency") or None
                salary_gross = salary.get("gross")

            schedule_name = None
            schedule = raw.get("schedule")
            if isinstance(schedule, dict):
                schedule_name = schedule.get("name") or None

            snippet_requirement = None
            snippet_responsibility = None
            snippet = raw.get("snippet")
            if isinstance(snippet, dict):
                snippet_requirement = snippet.get("requirement") or None
                snippet_responsibility = snippet.get("responsibility") or None

            vacancy_type_name = None
            vacancy_type = raw.get("type")
            if isinstance(vacancy_type, dict):
                vacancy_type_name = vacancy_type.get("name") or None

            response_letter_required = raw.get("response_letter_required")
            has_test = raw.get("has_test")

            address_city = None
            address_street = None
            address = raw.get("address")
            if isinstance(address, dict):
                address_city = address.get("city") or None
                address_street = address.get("street") or None

            professional_roles: list[str] = []
            roles = raw.get("professional_roles")
            if isinstance(roles, list):
                for role in roles:
                    if isinstance(role, dict):
                        role_name = role.get("name")
                        if isinstance(role_name, str):
                            professional_roles.append(role_name)

            items.append(
                VacancyListItem(
                    vacancy_id=vacancy_id,
                    name=name,
                    area_name=area_name,
                    publication_time_iso=publication_time_iso,
                    alternate_url=alternate_url,
                    company_name=company_name,
                    salary_from=salary_from,
                    salary_to=salary_to,
                    salary_currency=salary_currency,
                    salary_gross=salary_gross,
                    schedule_name=schedule_name,
                    snippet_requirement=snippet_requirement,
                    snippet_responsibility=snippet_responsibility,
                    vacancy_type_name=vacancy_type_name,
                    response_letter_required=response_letter_required,
                    has_test=has_test,
                    address_city=address_city,
                    address_street=address_street,
                    professional_roles=professional_roles if professional_roles else None,
                )
            )

        result = VacancyList(items=items)
        
        if return_cookies:
            return result, updated_cookies
        return result

    async def fetch_vacancy_list_front(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        query: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        return_cookies: bool = False,
    ) -> VacancyList | tuple[VacancyList, Dict[str, str]]:
        """Получить список вакансий через внутренний API /search/vacancy."""
        base_url = internal_api_base_url.rstrip("/")
        url = f"{base_url}/search/vacancy"

        # Обязательные заголовки для внутреннего API
        enhanced_headers = dict(headers)
        enhanced_headers.setdefault("Accept", "application/json")
        enhanced_headers.setdefault("X-Requested-With", "XMLHttpRequest")

        # Добавляем XSRF токен в заголовки, если есть в cookies
        xsrf_token = cookies.get("_xsrf")
        if xsrf_token:
            enhanced_headers.setdefault("X-Xsrftoken", xsrf_token)

        print(f"[list-front] GET {url} params={query}", flush=True)
        print(f"[list-front] Query data: {json.dumps(query, indent=2, ensure_ascii=False)}", flush=True)
        print(f"[list-front] Headers keys: {list(enhanced_headers.keys())}", flush=True)
        print(f"[list-front] XSRF token: {xsrf_token[:50] if xsrf_token else 'NOT_FOUND'}", flush=True)

        async with httpx.AsyncClient(
            headers=enhanced_headers, cookies=cookies, timeout=self._timeout
        ) as client:
            try:
                resp = await client.get(url, params=query)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                print(
                    f"[list-front] HTTP {response.status_code} for {response.request.url}",
                    flush=True,
                )
                ct = response.headers.get("Content-Type", "")
                print(f"[list-front] Content-Type: {ct}", flush=True)
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                print(f"[list-front] Body preview: {body_preview}", flush=True)
                raise

            try:
                payload = resp.json()
            except json.JSONDecodeError as exc:
                text = resp.text
                print(
                    f"[list-front] Не удалось распарсить JSON: {exc}; body_len={len(text)}",
                    flush=True,
                )
                raise RuntimeError(
                    f"Не удалось распарсить JSON ответа /search/vacancy: {exc}; body_len={len(text)}"
                ) from exc

            # Извлечь обновленные cookies после запроса
            updated_cookies = self._extract_cookies(client)

        # Структура внутреннего API: vacancySearchResult -> vacancies: [ { vacancyId, name, company, ... } ]
        vacancy_search_result = payload.get("vacancySearchResult")
        if not isinstance(vacancy_search_result, dict):
            raise RuntimeError(
                "[list-front] Ожидался объект vacancySearchResult в корне ответа"
            )

        raw_vacancies = vacancy_search_result.get("vacancies") or []
        if not isinstance(raw_vacancies, list):
            raw_vacancies = []

        # Создаем справочник professional_role ID -> название для маппинга
        professional_role_map: Dict[int, str] = {}
        professional_role_clusters = payload.get("vacancySearchDictionaries", {}).get("professional_role")
        if isinstance(professional_role_clusters, dict):
            groups = professional_role_clusters.get("groups")
            if isinstance(groups, dict):
                for role_id_str, role_data in groups.items():
                    if isinstance(role_data, dict):
                        role_title = role_data.get("title")
                        if isinstance(role_title, str):
                            try:
                                role_id = int(role_id_str)
                                professional_role_map[role_id] = role_title
                            except (ValueError, TypeError):
                                pass

        items: list[VacancyListItem] = []
        for raw in raw_vacancies:
            if not isinstance(raw, dict):
                continue

            # vacancyId во внутреннем API - число
            vacancy_id = raw.get("vacancyId")
            if not isinstance(vacancy_id, int):
                continue

            name = raw.get("name") or ""

            # Компания
            company_name = None
            company = raw.get("company")
            if isinstance(company, dict):
                company_name = company.get("visibleName") or company.get("name") or None

            # Публикация - берем из publicationTime
            publication_time_iso = None
            publication_time = raw.get("publicationTime")
            if isinstance(publication_time, dict):
                publication_time_iso = publication_time.get("$") or None

            # Ссылка
            alternate_url = None
            links = raw.get("links")
            if isinstance(links, dict):
                alternate_url = links.get("desktop") or None

            # Зарплата - структура compensation может быть разной
            salary_from = None
            salary_to = None
            salary_currency = None
            salary_gross = None
            compensation = raw.get("compensation")
            if isinstance(compensation, dict):
                # Проверяем, есть ли noCompensation (зарплата не указана)
                # noCompensation может быть пустым объектом {} - это означает, что зарплата не указана
                has_no_compensation = "noCompensation" in compensation
                
                # Если нет noCompensation, парсим зарплату
                if not has_no_compensation:
                    # Пытаемся получить from/to
                    from_val = compensation.get("from")
                    if from_val is not None:
                        try:
                            if isinstance(from_val, (int, float)):
                                salary_from = int(from_val)
                            elif isinstance(from_val, str) and from_val.strip():
                                salary_from = int(from_val)
                        except (ValueError, TypeError):
                            pass  # salary_from остается None
                    
                    to_val = compensation.get("to")
                    if to_val is not None:
                        try:
                            if isinstance(to_val, (int, float)):
                                salary_to = int(to_val)
                            elif isinstance(to_val, str) and to_val.strip():
                                salary_to = int(to_val)
                        except (ValueError, TypeError):
                            pass  # salary_to остается None
                    
                    # Во внутреннем API используется currencyCode (не currency)
                    salary_currency = compensation.get("currencyCode")
                    if not salary_currency:
                        salary_currency = compensation.get("currency")
                    
                    # gross - булево значение (может отсутствовать)
                    gross_val = compensation.get("gross")
                    if isinstance(gross_val, bool):
                        salary_gross = gross_val

            # Регион
            area_name = None
            area = raw.get("area")
            if isinstance(area, dict):
                area_name = area.get("name") or None

            # Адрес - может отсутствовать (например, только contactInfo: null)
            address_city = None
            address_street = None
            address = raw.get("address")
            if address is not None and isinstance(address, dict):
                # city и street могут быть пустыми строками, проверяем на None
                city_val = address.get("city")
                if isinstance(city_val, str) and city_val:
                    address_city = city_val
                
                street_val = address.get("street")
                if isinstance(street_val, str) and street_val:
                    address_street = street_val

            # График работы - из @workSchedule (например, "remote", "fullDay")
            schedule_name = None
            work_schedule_attr = raw.get("@workSchedule")
            if isinstance(work_schedule_attr, str) and work_schedule_attr.strip():
                # @workSchedule содержит коды типа "remote", "fullDay" и т.д.
                schedule_name = work_schedule_attr
            # Если нет @workSchedule, можно попробовать из workScheduleByDays
            # но там коды типа "FIVE_ON_TWO_OFF", что менее читаемо
            if not schedule_name:
                work_schedule_by_days = raw.get("workScheduleByDays")
                if isinstance(work_schedule_by_days, list) and work_schedule_by_days:
                    schedule_elem = work_schedule_by_days[0]
                    if isinstance(schedule_elem, dict):
                        schedule_elements = schedule_elem.get("workScheduleByDaysElement")
                        if isinstance(schedule_elements, list) and schedule_elements:
                            first_elem = schedule_elements[0]
                            if isinstance(first_elem, str) and first_elem:
                                schedule_name = first_elem

            # Профессиональные роли - из professionalRoleIds получаем ID, затем маппим на названия из справочника
            professional_roles: list[str] = []
            professional_role_ids_list = raw.get("professionalRoleIds")
            if isinstance(professional_role_ids_list, list):
                for role_item in professional_role_ids_list:
                    if isinstance(role_item, dict):
                        role_id_list = role_item.get("professionalRoleId")
                        if isinstance(role_id_list, list):
                            for role_id in role_id_list:
                                if isinstance(role_id, int):
                                    role_name = professional_role_map.get(role_id)
                                    if role_name and role_name not in professional_roles:
                                        professional_roles.append(role_name)
                                elif isinstance(role_id, str):
                                    try:
                                        role_id_int = int(role_id)
                                        role_name = professional_role_map.get(role_id_int)
                                        if role_name and role_name not in professional_roles:
                                            professional_roles.append(role_name)
                                    except (ValueError, TypeError):
                                        pass

            # Сниппеты требований/обязанностей
            # Когда enable_snippets=true, в вакансии появляется поле snippet
            snippet_requirement = None
            snippet_responsibility = None
            snippet = raw.get("snippet")
            if isinstance(snippet, dict):
                # req - требования (requirement)
                req_val = snippet.get("req")
                if isinstance(req_val, str) and req_val.strip():
                    snippet_requirement = req_val.strip()
                
                # resp - обязанности (responsibility)
                resp_val = snippet.get("resp")
                if isinstance(resp_val, str) and resp_val.strip():
                    snippet_responsibility = resp_val.strip()
                
                # Также доступны cond (условия), skill (навыки), desc (описание)
                # но они не сохраняются в VacancyListItem, так как там нет соответствующих полей

            # responseLetterRequired - из атрибута @responseLetterRequired
            response_letter_required = raw.get("@responseLetterRequired")
            if not isinstance(response_letter_required, bool):
                response_letter_required = None

            # has_test - может быть userTestPresent
            has_test = raw.get("userTestPresent")
            if not isinstance(has_test, bool):
                has_test = None

            # Тип вакансии - во внутреннем API может быть в разных местах
            # Например, в employmentForm или других полях
            vacancy_type_name = None
            employment_form = raw.get("employmentForm")
            if isinstance(employment_form, str) and employment_form:
                vacancy_type_name = employment_form
            # Также можно взять из employment.@type
            if not vacancy_type_name:
                employment = raw.get("employment")
                if isinstance(employment, dict):
                    emp_type = employment.get("@type")
                    if isinstance(emp_type, str) and emp_type:
                        vacancy_type_name = emp_type

            items.append(
                VacancyListItem(
                    vacancy_id=vacancy_id,
                    name=name,
                    area_name=area_name,
                    publication_time_iso=publication_time_iso,
                    alternate_url=alternate_url,
                    company_name=company_name,
                    salary_from=salary_from,
                    salary_to=salary_to,
                    salary_currency=salary_currency,
                    salary_gross=salary_gross,
                    schedule_name=schedule_name,
                    snippet_requirement=snippet_requirement,
                    snippet_responsibility=snippet_responsibility,
                    vacancy_type_name=vacancy_type_name,
                    response_letter_required=response_letter_required,
                    has_test=has_test,
                    address_city=address_city,
                    address_street=address_street,
                    professional_roles=professional_roles if professional_roles else None,
                )
            )

        result = VacancyList(items=items)
        
        if return_cookies:
            return result, updated_cookies
        return result

    async def fetch_areas(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        return_cookies: bool = False,
    ) -> List[Dict[str, Any]] | tuple[List[Dict[str, Any]], Dict[str, str]]:
        """Получить дерево регионов по /areas."""

        url = f"{self._base_url}/areas"

        async with httpx.AsyncClient(headers=headers, cookies=cookies, timeout=self._timeout) as client:
            try:
                resp = await client.get(url)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                print(
                    f"[areas] HTTP {response.status_code} for {response.request.url}",
                    flush=True,
                )
                ct = response.headers.get("Content-Type", "")
                print(f"[areas] Content-Type: {ct}", flush=True)
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                print(f"[areas] Body preview: {body_preview}", flush=True)
                raise

            try:
                payload = resp.json()
            except json.JSONDecodeError as exc:  # pragma: no cover - диагностика
                text = resp.text
                print(
                    f"[areas] Не удалось распарсить JSON дерева регионов: {exc}; body_len={len(text)}",
                    flush=True,
                )
                raise RuntimeError(
                    f"Не удалось распарсить JSON дерева регионов: {exc}; body_len={len(text)}"
                ) from exc

            # Извлечь обновленные cookies после запроса
            updated_cookies = self._extract_cookies(client)

        # /areas возвращает корневой массив регионов (страны), у каждой могут быть дочерние areas.
        if not isinstance(payload, list):
            raise RuntimeError("[areas] Ожидался список регионов в корне ответа")

        if return_cookies:
            return payload, updated_cookies
        return payload

    async def fetch_vacancy_detail(
        self,
        vacancy_id: int,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        return_cookies: bool = False,
    ) -> Optional[VacancyDetail] | tuple[Optional[VacancyDetail], Dict[str, str]]:
        # Публичное API: GET /vacancies/{id}
        url = f"{self._base_url}/vacancies/{vacancy_id}"

        async with httpx.AsyncClient(headers=headers, cookies=cookies, timeout=self._timeout) as client:
            try:
                resp = await client.get(url)
            except httpx.HTTPError as exc:  # pragma: no cover - сетевые ошибки
                print(f"[detail] vacancyId={vacancy_id}: HTTP ошибка {exc}", flush=True)
                if return_cookies:
                    updated_cookies = self._extract_cookies(client)
                    return None, updated_cookies
                return None

            if resp.status_code != 200:
                print(
                    f"[detail] vacancyId={vacancy_id}: неожиданный статус HTTP {resp.status_code}",
                    flush=True,
                )
                if return_cookies:
                    updated_cookies = self._extract_cookies(client)
                    return None, updated_cookies
                return None

            try:
                payload = resp.json()
            except json.JSONDecodeError:
                text = resp.text
                print(
                    f"[detail] vacancyId={vacancy_id}: ответ не JSON, длина={len(text)}",
                    flush=True,
                )
                if return_cookies:
                    updated_cookies = self._extract_cookies(client)
                    return None, updated_cookies
                return None

            # Извлечь обновленные cookies после запроса
            updated_cookies = self._extract_cookies(client)

        # Публичное API возвращает детальную вакансию целиком в корне payload
        try:
            result = self._map_vacancy_view_to_detail(payload)
            if return_cookies:
                return result, updated_cookies
            return result
        except Exception as exc:
            print(f"[detail] vacancyId={vacancy_id}: ошибка маппинга детали: {exc}", flush=True)
            if return_cookies:
                return None, updated_cookies
            return None

    @staticmethod
    def _map_vacancy_view_to_detail(v: Dict[str, object]) -> VacancyDetail:
        """Маппинг детальной вакансии из публичного API /vacancies/{id} в доменную модель."""

        raw_id = v.get("id")
        try:
            vacancy_id = int(raw_id)
        except (TypeError, ValueError):
            raise ValueError("vacancy.id отсутствует или не число")

        name = str(v.get("name") or "")

        company_name: Optional[str] = None
        employer = v.get("employer")
        if isinstance(employer, dict):
            company_name = employer.get("name") or None

        area_name: Optional[str] = None
        area = v.get("area")
        if isinstance(area, dict):
            area_name = area.get("name") or None

        # Преобразуем salary в человекочитаемую строку
        compensation_str: Optional[str] = None
        salary = v.get("salary")
        if isinstance(salary, dict):
            comp_from = salary.get("from")
            comp_to = salary.get("to")
            currency = salary.get("currency") or ""
            parts: list[str] = []
            if isinstance(comp_from, (int, float)):
                parts.append(f"от {comp_from}")
            if isinstance(comp_to, (int, float)):
                parts.append(f"до {comp_to}")
            if currency:
                parts.append(str(currency))
            compensation_str = " ".join(parts) if parts else "зарплата не указана"

        publication_date_str: Optional[str] = None
        published_at = v.get("published_at")
        if isinstance(published_at, str):
            publication_date_str = published_at

        work_experience: Optional[str] = None
        experience = v.get("experience")
        if isinstance(experience, dict):
            work_experience = experience.get("name") or None

        employment: Optional[str] = None
        employment_obj = v.get("employment")
        if isinstance(employment_obj, dict):
            employment = employment_obj.get("name") or None

        work_formats: list[str] = []
        raw_work_formats = v.get("work_format") or []
        if isinstance(raw_work_formats, list):
            for wf in raw_work_formats:
                if isinstance(wf, dict):
                    name_val = wf.get("name")
                    if isinstance(name_val, str):
                        work_formats.append(name_val)

        schedule_by_days: list[str] = []
        raw_schedule = v.get("work_schedule_by_days") or []
        if isinstance(raw_schedule, list):
            for sch in raw_schedule:
                if isinstance(sch, dict):
                    name_val = sch.get("name")
                    if isinstance(name_val, str):
                        schedule_by_days.append(name_val)

        working_hours: list[str] = []
        raw_hours = v.get("working_hours") or []
        if isinstance(raw_hours, list):
            for wh in raw_hours:
                if isinstance(wh, dict):
                    name_val = wh.get("name")
                    if isinstance(name_val, str):
                        working_hours.append(name_val)

        link = v.get("alternate_url") or f"https://hh.ru/vacancy/{vacancy_id}"

        description_html = v.get("description")
        if isinstance(description_html, str):
            description_html_str = description_html
        else:
            description_html_str = None

        key_skills_list: list[str] = []
        key_skills = v.get("key_skills")
        if isinstance(key_skills, list):
            for ks in key_skills:
                if isinstance(ks, dict):
                    name_val = ks.get("name")
                    if isinstance(name_val, str):
                        key_skills_list.append(name_val)

        return VacancyDetail(
            vacancy_id=vacancy_id,
            name=name,
            company_name=company_name,
            area_name=area_name,
            compensation=compensation_str,
            publication_date=publication_date_str,
            work_experience=work_experience,
            employment=employment,
            work_formats=list(work_formats),
            schedule_by_days=list(schedule_by_days),
            working_hours=list(working_hours),
            link=link,
            key_skills=key_skills_list,
            description_html=description_html_str,
        )

    async def respond_to_vacancy(
        self,
        vacancy_id: int,
        resume_hash: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        ignore_postponed: bool = True,
        incomplete: bool = False,
        mark_applicant_visible_in_vacancy_country: bool = False,
        country_ids: List[str] | None = None,
        letter: str = "1",
        lux: bool = True,
        without_test: str = "no",
        hhtm_from_label: str = "",
        hhtm_source_label: str = "",
        return_cookies: bool = False,
    ) -> Dict[str, Any] | tuple[Dict[str, Any], Dict[str, str]]:
        """Откликнуться на вакансию по /applicant/vacancy_response/popup."""
        base_url = internal_api_base_url.rstrip("/")
        url = f"{base_url}/applicant/vacancy_response/popup"

        # Извлекаем _xsrf из cookies или headers
        xsrf_token = cookies.get("_xsrf") or headers.get("x-xsrftoken") or headers.get("X-Xsrftoken") or ""

        # Подготавливаем form-data
        form_data: Dict[str, Any] = {
            "_xsrf": xsrf_token,
            "vacancy_id": str(vacancy_id),
            "resume_hash": resume_hash,
            "ignore_postponed": "true" if ignore_postponed else "false",
            "incomplete": "true" if incomplete else "false",
            "mark_applicant_visible_in_vacancy_country": "true" if mark_applicant_visible_in_vacancy_country else "false",
            "country_ids": json.dumps(country_ids) if country_ids else "[]",
            "letter": letter,
            "lux": "true" if lux else "false",
            "withoutTest": without_test,
            "hhtmFromLabel": hhtm_from_label,
            "hhtmSourceLabel": hhtm_source_label,
        }

        print(f"[respond] POST {url} vacancy_id={vacancy_id} resume_hash={resume_hash}", flush=True)
        print(f"[respond] Form data: {json.dumps(form_data, indent=2, ensure_ascii=False)}", flush=True)
        print(f"[respond] Headers keys: {list(headers.keys())}", flush=True)
        print(f"[respond] Cookies keys: {list(cookies.keys())}", flush=True)
        print(f"[respond] XSRF token: {xsrf_token[:50] if xsrf_token else 'NOT_FOUND'}", flush=True)

        async with httpx.AsyncClient(headers=headers, cookies=cookies, timeout=self._timeout) as client:
            try:
                resp = await client.post(url, data=form_data)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                print(
                    f"[respond] HTTP {response.status_code} for {response.request.url}",
                    flush=True,
                )
                ct = response.headers.get("Content-Type", "")
                print(f"[respond] Content-Type: {ct}", flush=True)
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                print(f"[respond] Body preview: {body_preview}", flush=True)
                raise

            try:
                payload = resp.json()
            except json.JSONDecodeError as exc:
                text = resp.text
                print(
                    f"[respond] Не удалось распарсить JSON ответа: {exc}; body_len={len(text)}",
                    flush=True,
                )
                raise RuntimeError(
                    f"Не удалось распарсить JSON ответа отклика: {exc}; body_len={len(text)}"
                ) from exc

            # Извлечь обновленные cookies после запроса
            updated_cookies = self._extract_cookies(client)

        if return_cookies:
            return payload, updated_cookies
        return payload

    async def fetch_resumes(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        return_cookies: bool = False,
    ) -> List[HHResume] | tuple[List[HHResume], Dict[str, str]]:
        """Получить список резюме пользователя по /applicant/resumes."""
        base_url = internal_api_base_url.rstrip("/")
        url = f"{base_url}/applicant/resumes"

        print(f"[resumes] GET {url}", flush=True)

        async with httpx.AsyncClient(headers=headers, cookies=cookies, timeout=self._timeout) as client:
            try:
                resp = await client.get(url)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                print(
                    f"[resumes] HTTP {response.status_code} for {response.request.url}",
                    flush=True,
                )
                ct = response.headers.get("Content-Type", "")
                print(f"[resumes] Content-Type: {ct}", flush=True)
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                print(f"[resumes] Body preview: {body_preview}", flush=True)
                raise

            try:
                payload = resp.json()
            except json.JSONDecodeError as exc:
                text = resp.text
                print(
                    f"[resumes] Не удалось распарсить JSON ответа: {exc}; body_len={len(text)}",
                    flush=True,
                )
                raise RuntimeError(
                    f"Не удалось распарсить JSON ответа списка резюме: {exc}; body_len={len(text)}"
                ) from exc

            # Извлечь обновленные cookies после запроса
            updated_cookies = self._extract_cookies(client)

        # Извлекаем массив резюме из applicantResumes
        raw_resumes = payload.get("applicantResumes") or []
        if not isinstance(raw_resumes, list):
            raise RuntimeError("[resumes] Ожидался список резюме в applicantResumes")

        resumes: list[HHResume] = []
        for raw in raw_resumes:
            if not isinstance(raw, dict):
                continue

            try:
                resume = self._map_resume_view_to_entity(raw)
                resumes.append(resume)
            except Exception as exc:
                print(f"[resumes] Ошибка маппинга резюме: {exc}", flush=True)
                continue

        if return_cookies:
            return resumes, updated_cookies
        return resumes

    async def fetch_resume_detail(
        self,
        resume_hash: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        return_cookies: bool = False,
    ) -> Optional[HHResumeDetailed] | tuple[Optional[HHResumeDetailed], Dict[str, str]]:
        """Получить детальное резюме по /resume/{hash}."""
        base_url = internal_api_base_url.rstrip("/")
        url = f"{base_url}/resume/{resume_hash}"

        print(f"[resume_detail] GET {url} hash={resume_hash}", flush=True)

        async with httpx.AsyncClient(headers=headers, cookies=cookies, timeout=self._timeout) as client:
            try:
                resp = await client.get(url)
            except httpx.HTTPError as exc:
                print(f"[resume_detail] hash={resume_hash}: HTTP ошибка {exc}", flush=True)
                if return_cookies:
                    updated_cookies = self._extract_cookies(client)
                    return None, updated_cookies
                return None

            if resp.status_code != 200:
                print(
                    f"[resume_detail] hash={resume_hash}: неожиданный статус HTTP {resp.status_code}",
                    flush=True,
                )
                if return_cookies:
                    updated_cookies = self._extract_cookies(client)
                    return None, updated_cookies
                return None

            try:
                payload = resp.json()
            except json.JSONDecodeError:
                text = resp.text
                print(
                    f"[resume_detail] hash={resume_hash}: ответ не JSON, длина={len(text)}",
                    flush=True,
                )
                if return_cookies:
                    updated_cookies = self._extract_cookies(client)
                    return None, updated_cookies
                return None

            # Извлечь обновленные cookies после запроса
            updated_cookies = self._extract_cookies(client)

        # Данные резюме находятся в applicantResume
        applicant_resume = payload.get("applicantResume")
        if not isinstance(applicant_resume, dict):
            print(f"[resume_detail] hash={resume_hash}: applicantResume отсутствует или не является словарем", flush=True)
            if return_cookies:
                return None, updated_cookies
            return None

        try:
            result = self._map_resume_detail_view_to_entity(applicant_resume)
            if return_cookies:
                return result, updated_cookies
            return result
        except Exception as exc:
            print(f"[resume_detail] hash={resume_hash}: ошибка маппинга детального резюме: {exc}", flush=True)
            if return_cookies:
                return None, updated_cookies
            return None

    @staticmethod
    def _map_resume_view_to_entity(r: Dict[str, object]) -> HHResume:
        """Маппинг резюме из /applicant/resumes в доменную модель."""
        attrs = r.get("_attributes")
        if not isinstance(attrs, dict):
            raise ValueError("_attributes отсутствует или не является словарем")

        resume_id = attrs.get("id")
        if not isinstance(resume_id, str):
            raise ValueError("resume.id отсутствует или не строка")

        hash_val = attrs.get("hash")
        if not isinstance(hash_val, str):
            raise ValueError("resume.hash отсутствует или не строка")

        # Заголовок резюме
        title = ""
        title_list = r.get("title")
        if isinstance(title_list, list) and len(title_list) > 0:
            title_obj = title_list[0]
            if isinstance(title_obj, dict):
                title = str(title_obj.get("string", ""))

        # Статус
        status = attrs.get("status")
        status_str = str(status) if status is not None else None

        # Регион
        area_name: Optional[str] = None
        area_list = r.get("area")
        if isinstance(area_list, list) and len(area_list) > 0:
            area_obj = area_list[0]
            if isinstance(area_obj, dict):
                area_name = area_obj.get("title")
                if isinstance(area_name, str):
                    pass  # уже строка
                else:
                    area_name = None

        # Зарплата
        salary_amount: Optional[int] = None
        salary_currency: Optional[str] = None
        salary_list = r.get("salary")
        if isinstance(salary_list, list) and len(salary_list) > 0:
            salary_obj = salary_list[0]
            if isinstance(salary_obj, dict):
                amount = salary_obj.get("amount")
                if isinstance(amount, (int, float)):
                    salary_amount = int(amount)
                currency = salary_obj.get("currency")
                if isinstance(currency, str):
                    salary_currency = currency

        # Доступность для поиска
        is_searchable = attrs.get("isSearchable", True)
        if not isinstance(is_searchable, bool):
            is_searchable = True

        # Навыки
        key_skills: list[str] = []
        skills_list = r.get("keySkills")
        if isinstance(skills_list, list):
            for skill_obj in skills_list:
                if isinstance(skill_obj, dict):
                    skill_str = skill_obj.get("string")
                    if isinstance(skill_str, str):
                        key_skills.append(skill_str)

        # Профессиональная роль
        professional_role_id: Optional[int] = None
        role_list = r.get("professionalRole")
        if isinstance(role_list, list) and len(role_list) > 0:
            role_obj = role_list[0]
            if isinstance(role_obj, dict):
                role_val = role_obj.get("string")
                if isinstance(role_val, (int, str)):
                    try:
                        professional_role_id = int(role_val)
                    except (TypeError, ValueError):
                        pass

        # Опыт работы (в месяцах)
        total_experience_months: Optional[int] = None
        exp_list = r.get("totalExperience")
        if isinstance(exp_list, list) and len(exp_list) > 0:
            exp_obj = exp_list[0]
            if isinstance(exp_obj, dict):
                exp_val = exp_obj.get("string")
                if isinstance(exp_val, (int, str)):
                    try:
                        total_experience_months = int(exp_val)
                    except (TypeError, ValueError):
                        pass

        # Timestamps
        updated_ts = attrs.get("updated")
        updated_timestamp = int(updated_ts) if isinstance(updated_ts, (int, float)) else None

        created_ts = attrs.get("created")
        created_timestamp = int(created_ts) if isinstance(created_ts, (int, float)) else None

        last_edit_ts = attrs.get("lastEditTime")
        last_edit_time = int(last_edit_ts) if isinstance(last_edit_ts, (int, float)) else None

        return HHResume(
            resume_id=resume_id,
            hash=hash_val,
            title=title,
            status=status_str,
            area_name=area_name,
            salary_amount=salary_amount,
            salary_currency=salary_currency,
            is_searchable=is_searchable,
            key_skills=key_skills if key_skills else None,
            professional_role_id=professional_role_id,
            total_experience_months=total_experience_months,
            updated_timestamp=updated_timestamp,
            created_timestamp=created_timestamp,
            last_edit_time=last_edit_time,
        )

    @staticmethod
    def _map_resume_detail_view_to_entity(r: Dict[str, object]) -> HHResumeDetailed:
        """Маппинг детального резюме из /resume/{hash} в доменную модель."""
        attrs = r.get("_attributes")
        if not isinstance(attrs, dict):
            raise ValueError("_attributes отсутствует или не является словарем")

        resume_id = attrs.get("id")
        if not isinstance(resume_id, str):
            raise ValueError("resume.id отсутствует или не строка")

        hash_val = attrs.get("hash")
        if not isinstance(hash_val, str):
            raise ValueError("resume.hash отсутствует или не строка")

        # Заголовок резюме
        title = ""
        title_list = r.get("title")
        if isinstance(title_list, list) and len(title_list) > 0:
            title_obj = title_list[0]
            if isinstance(title_obj, dict):
                title = str(title_obj.get("string", ""))

        # Личная информация
        first_name: Optional[str] = None
        first_name_list = r.get("firstName")
        if isinstance(first_name_list, list) and len(first_name_list) > 0:
            first_name_obj = first_name_list[0]
            if isinstance(first_name_obj, dict):
                fn_val = first_name_obj.get("string")
                if isinstance(fn_val, str):
                    first_name = fn_val

        last_name: Optional[str] = None
        last_name_list = r.get("lastName")
        if isinstance(last_name_list, list) and len(last_name_list) > 0:
            last_name_obj = last_name_list[0]
            if isinstance(last_name_obj, dict):
                ln_val = last_name_obj.get("string")
                if isinstance(ln_val, str):
                    last_name = ln_val

        middle_name: Optional[str] = None
        middle_name_list = r.get("middleName")
        if isinstance(middle_name_list, list) and len(middle_name_list) > 0:
            middle_name_obj = middle_name_list[0]
            if isinstance(middle_name_obj, dict):
                mn_val = middle_name_obj.get("string")
                if isinstance(mn_val, str) and mn_val:
                    middle_name = mn_val

        # Статус
        status = attrs.get("status")
        status_str = str(status) if status is not None else None

        # Регион
        area_name: Optional[str] = None
        area_list = r.get("area")
        if isinstance(area_list, list) and len(area_list) > 0:
            area_obj = area_list[0]
            if isinstance(area_obj, dict):
                # В детальном резюме может быть title или string
                area_title = area_obj.get("title")
                if isinstance(area_title, str):
                    area_name = area_title
                else:
                    # Если нет title, пробуем получить по string ID и потом найти название
                    area_id = area_obj.get("string")
                    if area_id is not None:
                        area_name = None  # Без дополнительного запроса не можем получить название

        # Зарплата
        salary_amount: Optional[int] = None
        salary_currency: Optional[str] = None
        salary_list = r.get("salary")
        if isinstance(salary_list, list) and len(salary_list) > 0:
            salary_obj = salary_list[0]
            if isinstance(salary_obj, dict):
                amount = salary_obj.get("amount")
                if isinstance(amount, (int, float)):
                    salary_amount = int(amount)
                currency = salary_obj.get("currency")
                if isinstance(currency, str):
                    salary_currency = currency

        # Доступность для поиска
        is_searchable = attrs.get("isSearchable", True)
        if not isinstance(is_searchable, bool):
            is_searchable = True

        # Навыки
        key_skills: list[str] = []
        skills_list = r.get("keySkills")
        if isinstance(skills_list, list):
            for skill_obj in skills_list:
                if isinstance(skill_obj, dict):
                    skill_str = skill_obj.get("string")
                    if isinstance(skill_str, str):
                        key_skills.append(skill_str)

        # Профессиональная роль
        professional_role_id: Optional[int] = None
        role_list = r.get("professionalRole")
        if isinstance(role_list, list) and len(role_list) > 0:
            role_obj = role_list[0]
            if isinstance(role_obj, dict):
                role_val = role_obj.get("string")
                if isinstance(role_val, (int, str)):
                    try:
                        professional_role_id = int(role_val)
                    except (TypeError, ValueError):
                        pass

        # Опыт работы (в месяцах)
        total_experience_months: Optional[int] = None
        exp_list = r.get("totalExperience")
        if isinstance(exp_list, list) and len(exp_list) > 0:
            exp_obj = exp_list[0]
            if isinstance(exp_obj, dict):
                exp_val = exp_obj.get("string")
                if isinstance(exp_val, (int, str)):
                    try:
                        total_experience_months = int(exp_val)
                    except (TypeError, ValueError):
                        pass

        # Опыт работы (детальный)
        work_experience: list[HHWorkExperience] = []
        experience_list = r.get("experience")
        if isinstance(experience_list, list):
            for exp_obj in experience_list:
                if not isinstance(exp_obj, dict):
                    continue
                try:
                    exp_id = exp_obj.get("id")
                    if not isinstance(exp_id, (int, str)):
                        continue
                    exp_id_int = int(exp_id)

                    company_name = exp_obj.get("companyName")
                    if not isinstance(company_name, str):
                        continue

                    position = exp_obj.get("position")
                    if not isinstance(position, str):
                        continue

                    description = exp_obj.get("description")
                    description_str = str(description) if isinstance(description, str) else None

                    start_date = exp_obj.get("startDate")
                    start_date_str = str(start_date) if isinstance(start_date, str) else None

                    end_date = exp_obj.get("endDate")
                    end_date_str = str(end_date) if isinstance(end_date, str) else None

                    duration_years: Optional[int] = None
                    duration_months: Optional[int] = None
                    interval = exp_obj.get("interval")
                    if isinstance(interval, dict):
                        years = interval.get("years")
                        months = interval.get("months")
                        if isinstance(years, (int, float)):
                            duration_years = int(years)
                        if isinstance(months, (int, float)):
                            duration_months = int(months)

                    work_experience.append(
                        HHWorkExperience(
                            id=exp_id_int,
                            company_name=company_name,
                            position=position,
                            description=description_str,
                            start_date=start_date_str,
                            end_date=end_date_str,
                            duration_years=duration_years,
                            duration_months=duration_months,
                        )
                    )
                except Exception as exc:
                    print(f"[resume_detail] Ошибка парсинга опыта работы: {exc}", flush=True)
                    continue

        # О себе (из skills, первый элемент)
        about: Optional[str] = None
        skills_array = r.get("skills")
        if isinstance(skills_array, list) and len(skills_array) > 0:
            skills_obj = skills_array[0]
            if isinstance(skills_obj, dict):
                about_val = skills_obj.get("string")
                if isinstance(about_val, str):
                    about = about_val

        # Timestamps
        updated_ts = attrs.get("updated")
        updated_timestamp = int(updated_ts) if isinstance(updated_ts, (int, float)) else None

        created_ts = attrs.get("created")
        created_timestamp = int(created_ts) if isinstance(created_ts, (int, float)) else None

        last_edit_ts = attrs.get("lastEditTime")
        last_edit_time = int(last_edit_ts) if isinstance(last_edit_ts, (int, float)) else None

        return HHResumeDetailed(
            resume_id=resume_id,
            hash=hash_val,
            title=title,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            status=status_str,
            area_name=area_name,
            salary_amount=salary_amount,
            salary_currency=salary_currency,
            is_searchable=is_searchable,
            key_skills=key_skills if key_skills else None,
            professional_role_id=professional_role_id,
            total_experience_months=total_experience_months,
            work_experience=work_experience if work_experience else None,
            about=about,
            updated_timestamp=updated_timestamp,
            created_timestamp=created_timestamp,
            last_edit_time=last_edit_time,
        )

    async def fetch_chat_list(
        self,
        chat_ids: List[int],
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        chatik_api_base_url: str = "https://chatik.hh.ru",
        return_cookies: bool = False,
    ) -> HHListChat | tuple[HHListChat, Dict[str, str]]:
        """Получить список чатов по /chatik/api/chats."""
        base_url = chatik_api_base_url.rstrip("/")
        url = f"{base_url}/chatik/api/chats"

        # Обязательные заголовки для chatik API
        enhanced_headers = dict(headers)
        enhanced_headers.setdefault("Accept", "application/json")
        enhanced_headers.setdefault("X-Requested-With", "XMLHttpRequest")

        # Добавляем XSRF токен в заголовки, если есть в cookies
        xsrf_token = cookies.get("_xsrf")
        if xsrf_token:
            enhanced_headers.setdefault("X-Xsrftoken", xsrf_token)

        # Формируем параметры запроса
        params: Dict[str, str] = {
            "do_not_track_session_events": "true",
        }
        # Добавляем ids только если список не пустой
        if chat_ids:
            params["ids"] = ",".join(str(chat_id) for chat_id in chat_ids)

        print(f"[chat_list] GET {url} params={params}", flush=True)

        async with httpx.AsyncClient(
            headers=enhanced_headers, cookies=cookies, timeout=self._timeout
        ) as client:
            try:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                print(
                    f"[chat_list] HTTP {response.status_code} for {response.request.url}",
                    flush=True,
                )
                ct = response.headers.get("Content-Type", "")
                print(f"[chat_list] Content-Type: {ct}", flush=True)
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                print(f"[chat_list] Body preview: {body_preview}", flush=True)
                raise

            try:
                payload = resp.json()
            except json.JSONDecodeError as exc:
                text = resp.text
                print(
                    f"[chat_list] Не удалось распарсить JSON: {exc}; body_len={len(text)}",
                    flush=True,
                )
                raise RuntimeError(
                    f"Не удалось распарсить JSON ответа /chatik/api/chats: {exc}; body_len={len(text)}"
                ) from exc

            # Извлечь обновленные cookies после запроса
            updated_cookies = self._extract_cookies(client)

        # Парсим ответ
        chats_data = payload.get("chats", {})
        raw_chats = chats_data.get("items", [])
        if not isinstance(raw_chats, list):
            raw_chats = []

        chats_display_info_raw = payload.get("chatsDisplayInfo", {})
        if not isinstance(chats_display_info_raw, dict):
            chats_display_info_raw = {}

        items: list[HHChatListItem] = []
        display_info: Dict[int, HHChatDisplayInfo] = {}

        # Парсим display info
        for chat_id_str, display_raw in chats_display_info_raw.items():
            if not isinstance(display_raw, dict):
                continue
            try:
                chat_id = int(chat_id_str)
                title = display_raw.get("title") or ""
                subtitle = display_raw.get("subtitle")
                icon = display_raw.get("icon")
                display_info[chat_id] = HHChatDisplayInfo(
                    title=title,
                    subtitle=subtitle,
                    icon=icon,
                )
            except (ValueError, TypeError):
                continue

        # Парсим чаты
        for raw in raw_chats:
            if not isinstance(raw, dict):
                continue

            try:
                chat_item = self._map_chat_list_item(raw)
                items.append(chat_item)
            except Exception as exc:
                print(f"[chat_list] Ошибка маппинга чата: {exc}", flush=True)
                continue

        result = HHListChat(items=items, display_info=display_info)
        
        if return_cookies:
            return result, updated_cookies
        return result

    async def fetch_chat_detail(
        self,
        chat_id: int,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        chatik_api_base_url: str = "https://chatik.hh.ru",
        return_cookies: bool = False,
    ) -> Optional[HHChatDetailed] | tuple[Optional[HHChatDetailed], Dict[str, str]]:
        """Получить детальную информацию о чате с сообщениями по /chatik/api/chat_data."""
        base_url = chatik_api_base_url.rstrip("/")
        url = f"{base_url}/chatik/api/chat_data"

        # Обязательные заголовки для chatik API
        enhanced_headers = dict(headers)
        enhanced_headers.setdefault("Accept", "application/json")
        enhanced_headers.setdefault("X-Requested-With", "XMLHttpRequest")

        # Добавляем XSRF токен в заголовки, если есть в cookies
        xsrf_token = cookies.get("_xsrf")
        if xsrf_token:
            enhanced_headers.setdefault("X-Xsrftoken", xsrf_token)

        # Формируем параметры запроса
        params: Dict[str, str] = {
            "chatId": str(chat_id),
            "do_not_track_session_events": "true",
        }

        print(f"[chat_detail] GET {url} chat_id={chat_id}", flush=True)

        async with httpx.AsyncClient(
            headers=enhanced_headers, cookies=cookies, timeout=self._timeout
        ) as client:
            try:
                resp = await client.get(url, params=params)
            except httpx.HTTPError as exc:
                print(f"[chat_detail] chat_id={chat_id}: HTTP ошибка {exc}", flush=True)
                if return_cookies:
                    updated_cookies = self._extract_cookies(client)
                    return None, updated_cookies
                return None

            if resp.status_code != 200:
                print(
                    f"[chat_detail] chat_id={chat_id}: неожиданный статус HTTP {resp.status_code}",
                    flush=True,
                )
                if return_cookies:
                    updated_cookies = self._extract_cookies(client)
                    return None, updated_cookies
                return None

            try:
                payload = resp.json()
            except json.JSONDecodeError:
                text = resp.text
                print(
                    f"[chat_detail] chat_id={chat_id}: ответ не JSON, длина={len(text)}",
                    flush=True,
                )
                if return_cookies:
                    updated_cookies = self._extract_cookies(client)
                    return None, updated_cookies
                return None

            # Извлечь обновленные cookies после запроса
            updated_cookies = self._extract_cookies(client)

        # Парсим ответ
        chat_data = payload.get("chat")
        if not isinstance(chat_data, dict):
            print(f"[chat_detail] chat_id={chat_id}: chat отсутствует или не является словарем", flush=True)
            if return_cookies:
                return None, updated_cookies
            return None

        try:
            result = self._map_chat_detailed(chat_data)
            if return_cookies:
                return result, updated_cookies
            return result
        except Exception as exc:
            print(f"[chat_detail] chat_id={chat_id}: ошибка маппинга детального чата: {exc}", flush=True)
            if return_cookies:
                return None, updated_cookies
            return None

    @staticmethod
    def _map_chat_message(raw: Dict[str, Any]) -> HHChatMessage:
        """Маппинг сообщения из API в доменную модель."""
        message_id = raw.get("id")
        if not isinstance(message_id, int):
            raise ValueError("message.id отсутствует или не число")

        chat_id = raw.get("chatId")
        if not isinstance(chat_id, int):
            raise ValueError("message.chatId отсутствует или не число")

        creation_time = raw.get("creationTime") or ""
        text = raw.get("text") or ""
        message_type = raw.get("type") or "SIMPLE"
        can_edit = raw.get("canEdit", False)
        can_delete = raw.get("canDelete", False)
        only_visible_for_my_type = raw.get("onlyVisibleForMyType", False)
        has_content = raw.get("hasContent", False)
        hidden = raw.get("hidden", False)

        workflow_transition_id = raw.get("workflowTransitionId")
        if not isinstance(workflow_transition_id, int):
            workflow_transition_id = None

        workflow_transition = None
        workflow_transition_raw = raw.get("workflowTransition")
        if isinstance(workflow_transition_raw, dict):
            wt_id = workflow_transition_raw.get("id")
            topic_id = workflow_transition_raw.get("topicId")
            applicant_state = workflow_transition_raw.get("applicantState")
            declined_by_applicant = workflow_transition_raw.get("declinedByApplicant", False)

            if isinstance(wt_id, int) and isinstance(topic_id, int) and isinstance(applicant_state, str):
                workflow_transition = HHWorkflowTransition(
                    id=wt_id,
                    topic_id=topic_id,
                    applicant_state=applicant_state,
                    declined_by_applicant=declined_by_applicant,
                )

        participant_display = None
        participant_display_raw = raw.get("participantDisplay")
        if isinstance(participant_display_raw, dict):
            name = participant_display_raw.get("name") or ""
            is_bot = participant_display_raw.get("isBot", False)
            participant_display = HHParticipantDisplay(name=name, is_bot=is_bot)

        participant_id = raw.get("participantId")
        if not isinstance(participant_id, str):
            participant_id = None

        resources = raw.get("resources")
        if not isinstance(resources, dict):
            resources = None

        return HHChatMessage(
            id=message_id,
            chat_id=chat_id,
            creation_time=creation_time,
            text=text,
            type=message_type,
            can_edit=can_edit,
            can_delete=can_delete,
            only_visible_for_my_type=only_visible_for_my_type,
            has_content=has_content,
            hidden=hidden,
            workflow_transition_id=workflow_transition_id,
            workflow_transition=workflow_transition,
            participant_display=participant_display,
            participant_id=participant_id,
            resources=resources,
        )

    @staticmethod
    def _map_chat_list_item(raw: Dict[str, Any]) -> HHChatListItem:
        """Маппинг элемента списка чатов из API в доменную модель."""
        chat_id = raw.get("id")
        if not isinstance(chat_id, int):
            raise ValueError("chat.id отсутствует или не число")

        chat_type = raw.get("type") or ""
        unread_count = raw.get("unreadCount", 0)
        if not isinstance(unread_count, int):
            unread_count = 0

        pinned = raw.get("pinned", False)
        notification_enabled = raw.get("notificationEnabled", True)
        creation_time = raw.get("creationTime") or ""
        idempotency_key = raw.get("idempotencyKey") or ""
        owner_violates_rules = raw.get("ownerViolatesRules", False)
        untrusted_employer_restrictions_applied = raw.get("untrustedEmployerRestrictionsApplied", False)
        current_participant_id = raw.get("currentParticipantId") or ""

        last_message = None
        last_message_raw = raw.get("lastMessage")
        if isinstance(last_message_raw, dict):
            try:
                last_message = HHHttpClient._map_chat_message(last_message_raw)
            except Exception:
                pass

        last_viewed_by_opponent_message_id = raw.get("lastViewedByOpponentMessageId")
        if not isinstance(last_viewed_by_opponent_message_id, int):
            last_viewed_by_opponent_message_id = None

        last_viewed_by_current_user_message_id = raw.get("lastViewedByCurrentUserMessageId")
        if not isinstance(last_viewed_by_current_user_message_id, int):
            last_viewed_by_current_user_message_id = None

        resources = raw.get("resources")
        if not isinstance(resources, dict):
            resources = None

        write_possibility = None
        write_possibility_raw = raw.get("writePossibility")
        if isinstance(write_possibility_raw, dict):
            name = write_possibility_raw.get("name") or ""
            write_disabled_reasons = write_possibility_raw.get("writeDisabledReasons", [])
            if not isinstance(write_disabled_reasons, list):
                write_disabled_reasons = []
            write_disabled_reason = write_possibility_raw.get("writeDisabledReason") or ""
            write_possibility = HHWritePossibility(
                name=name,
                write_disabled_reasons=write_disabled_reasons,
                write_disabled_reason=write_disabled_reason,
            )

        operations = None
        operations_raw = raw.get("operations")
        if isinstance(operations_raw, dict):
            enabled = operations_raw.get("enabled", [])
            if isinstance(enabled, list):
                operations = HHChatOperations(enabled=enabled)

        participants_ids = raw.get("participantsIds")
        if not isinstance(participants_ids, list):
            participants_ids = None

        online_until_time = raw.get("onlineUntilTime")
        if not isinstance(online_until_time, str):
            online_until_time = None

        last_activity_time = raw.get("lastActivityTime")
        if not isinstance(last_activity_time, str):
            last_activity_time = None

        block_chat_info = raw.get("blockChatInfo")
        if not isinstance(block_chat_info, list):
            block_chat_info = None

        return HHChatListItem(
            id=chat_id,
            type=chat_type,
            unread_count=unread_count,
            pinned=pinned,
            notification_enabled=notification_enabled,
            creation_time=creation_time,
            idempotency_key=idempotency_key,
            owner_violates_rules=owner_violates_rules,
            untrusted_employer_restrictions_applied=untrusted_employer_restrictions_applied,
            current_participant_id=current_participant_id,
            last_activity_time=last_activity_time,
            last_message=last_message,
            last_viewed_by_opponent_message_id=last_viewed_by_opponent_message_id,
            last_viewed_by_current_user_message_id=last_viewed_by_current_user_message_id,
            resources=resources,
            write_possibility=write_possibility,
            operations=operations,
            participants_ids=participants_ids,
            online_until_time=online_until_time,
            block_chat_info=block_chat_info,
        )

    @staticmethod
    def _map_chat_detailed(raw: Dict[str, Any]) -> HHChatDetailed:
        """Маппинг детального чата из API в доменную модель."""
        chat_id = raw.get("id")
        if not isinstance(chat_id, int):
            raise ValueError("chat.id отсутствует или не число")

        chat_type = raw.get("type") or ""
        unread_count = raw.get("unreadCount", 0)
        if not isinstance(unread_count, int):
            unread_count = 0

        pinned = raw.get("pinned", False)
        notification_enabled = raw.get("notificationEnabled", True)
        creation_time = raw.get("creationTime") or ""
        owner_violates_rules = raw.get("ownerViolatesRules", False)
        untrusted_employer_restrictions_applied = raw.get("untrustedEmployerRestrictionsApplied", False)
        current_participant_id = raw.get("currentParticipantId") or ""

        messages = None
        messages_raw = raw.get("messages")
        if isinstance(messages_raw, dict):
            items_raw = messages_raw.get("items", [])
            if isinstance(items_raw, list):
                message_items: list[HHChatMessage] = []
                for msg_raw in items_raw:
                    if isinstance(msg_raw, dict):
                        try:
                            message_items.append(HHHttpClient._map_chat_message(msg_raw))
                        except Exception:
                            continue
                has_more = messages_raw.get("hasMore", False)
                messages = HHChatMessages(items=message_items, has_more=has_more)

        last_viewed_by_opponent_message_id = raw.get("lastViewedByOpponentMessageId")
        if not isinstance(last_viewed_by_opponent_message_id, int):
            last_viewed_by_opponent_message_id = None

        last_viewed_by_current_user_message_id = raw.get("lastViewedByCurrentUserMessageId")
        if not isinstance(last_viewed_by_current_user_message_id, int):
            last_viewed_by_current_user_message_id = None

        resources = raw.get("resources")
        if not isinstance(resources, dict):
            resources = None

        write_possibility = raw.get("writePossibility")
        if not isinstance(write_possibility, dict):
            write_possibility = None

        operations = raw.get("operations")
        if not isinstance(operations, dict):
            operations = None

        participants_ids = raw.get("participantsIds")
        if not isinstance(participants_ids, list):
            participants_ids = None

        online_until_time = raw.get("onlineUntilTime")
        if not isinstance(online_until_time, str):
            online_until_time = None

        last_activity_time = raw.get("lastActivityTime")
        if not isinstance(last_activity_time, str):
            last_activity_time = None

        block_chat_info = raw.get("blockChatInfo")
        if not isinstance(block_chat_info, list):
            block_chat_info = None

        return HHChatDetailed(
            id=chat_id,
            type=chat_type,
            unread_count=unread_count,
            pinned=pinned,
            notification_enabled=notification_enabled,
            creation_time=creation_time,
            owner_violates_rules=owner_violates_rules,
            untrusted_employer_restrictions_applied=untrusted_employer_restrictions_applied,
            current_participant_id=current_participant_id,
            last_activity_time=last_activity_time,
            messages=messages,
            last_viewed_by_opponent_message_id=last_viewed_by_opponent_message_id,
            last_viewed_by_current_user_message_id=last_viewed_by_current_user_message_id,
            resources=resources,
            write_possibility=write_possibility,
            operations=operations,
            participants_ids=participants_ids,
            online_until_time=online_until_time,
            block_chat_info=block_chat_info,
        )

    async def touch_resume(
        self,
        resume_hash: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        undirectable: bool = True,
        return_cookies: bool = False,
    ) -> Dict[str, Any] | tuple[Dict[str, Any], Dict[str, str]]:
        """Поднять резюме в списке по /applicant/resumes/touch."""
        base_url = internal_api_base_url.rstrip("/")
        url = f"{base_url}/applicant/resumes/touch"

        # Обязательные заголовки для внутреннего API
        enhanced_headers = dict(headers)
        enhanced_headers.setdefault("Accept", "application/json")
        enhanced_headers.setdefault("X-Requested-With", "XMLHttpRequest")

        # Добавляем XSRF токен в заголовки, если есть в cookies
        xsrf_token = cookies.get("_xsrf")
        if xsrf_token:
            enhanced_headers.setdefault("X-Xsrftoken", xsrf_token)

        # Подготавливаем multipart/form-data
        form_data: Dict[str, Any] = {
            "resume": resume_hash,
            "undirectable": "true" if undirectable else "false",
        }

        print(f"[touch_resume] POST {url} resume_hash={resume_hash}", flush=True)
        print(f"[touch_resume] Form data: {json.dumps(form_data, indent=2, ensure_ascii=False)}", flush=True)
        print(f"[touch_resume] Headers keys: {list(enhanced_headers.keys())}", flush=True)
        print(f"[touch_resume] XSRF token: {xsrf_token[:50] if xsrf_token else 'NOT_FOUND'}", flush=True)

        async with httpx.AsyncClient(
            headers=enhanced_headers, cookies=cookies, timeout=self._timeout
        ) as client:
            try:
                resp = await client.post(url, data=form_data)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                print(
                    f"[touch_resume] HTTP {response.status_code} for {response.request.url}",
                    flush=True,
                )
                ct = response.headers.get("Content-Type", "")
                print(f"[touch_resume] Content-Type: {ct}", flush=True)
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                print(f"[touch_resume] Body preview: {body_preview}", flush=True)
                raise

            try:
                payload = resp.json()
            except json.JSONDecodeError as exc:
                text = resp.text
                print(
                    f"[touch_resume] Не удалось распарсить JSON ответа: {exc}; body_len={len(text)}",
                    flush=True,
                )
                raise RuntimeError(
                    f"Не удалось распарсить JSON ответа поднятия резюме: {exc}; body_len={len(text)}"
                ) from exc

            # Извлечь обновленные cookies после запроса
            updated_cookies = self._extract_cookies(client)

        if return_cookies:
            return payload, updated_cookies
        return payload


class _RateLimiter:
    """Простой async‑rate‑лимитер по количеству запросов в секунду.

    Использует минимальный интервал между запросами: 1 / requests_per_second.
    Все инстансы, создающие его, должны шарить объект, чтобы лимит был общий.
    """

    def __init__(self, requests_per_second: float) -> None:
        self._min_interval = 1.0 / requests_per_second
        self._lock = asyncio.Lock()
        self._last_ts: float = 0.0

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            wait_for = self._last_ts + self._min_interval - now
            if wait_for > 0:
                await asyncio.sleep(wait_for)
                now = time.monotonic()
            self._last_ts = now


class RateLimitedHHHttpClient(HHHttpClient):
    """HH‑клиент с ограничением на число запросов в секунду.

    По умолчанию: не более 10 запросов/секунду.
    """

    def __init__(
        self,
        base_url: str = "https://api.hh.ru",
        timeout: float = 30.0,
        requests_per_second: float = 1.0,
        limiter: _RateLimiter | None = None,
    ) -> None:
        super().__init__(base_url=base_url, timeout=timeout)
        self._limiter = limiter or _RateLimiter(requests_per_second)

    async def fetch_vacancy_list(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        query: Dict[str, str],
        *,
        return_cookies: bool = False,
    ) -> VacancyList | tuple[VacancyList, Dict[str, str]]:
        await self._limiter.acquire()
        return await super().fetch_vacancy_list(headers, cookies, query, return_cookies=return_cookies)

    async def fetch_vacancy_list_front(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        query: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        return_cookies: bool = False,
    ) -> VacancyList | tuple[VacancyList, Dict[str, str]]:
        await self._limiter.acquire()
        return await super().fetch_vacancy_list_front(
            headers, cookies, query, internal_api_base_url=internal_api_base_url, return_cookies=return_cookies
        )

    async def fetch_vacancy_detail(
        self,
        vacancy_id: int,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        return_cookies: bool = False,
    ) -> Optional[VacancyDetail] | tuple[Optional[VacancyDetail], Dict[str, str]]:
        await self._limiter.acquire()
        return await super().fetch_vacancy_detail(vacancy_id, headers, cookies, return_cookies=return_cookies)

    async def fetch_areas(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        return_cookies: bool = False,
    ) -> List[Dict[str, Any]] | tuple[List[Dict[str, Any]], Dict[str, str]]:
        await self._limiter.acquire()
        return await super().fetch_areas(headers, cookies, return_cookies=return_cookies)

    async def respond_to_vacancy(
        self,
        vacancy_id: int,
        resume_hash: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        ignore_postponed: bool = True,
        incomplete: bool = False,
        mark_applicant_visible_in_vacancy_country: bool = False,
        country_ids: List[str] | None = None,
        letter: str = "1",
        lux: bool = True,
        without_test: str = "no",
        hhtm_from_label: str = "",
        hhtm_source_label: str = "",
        return_cookies: bool = False,
    ) -> Dict[str, Any] | tuple[Dict[str, Any], Dict[str, str]]:
        await self._limiter.acquire()
        return await super().respond_to_vacancy(
            vacancy_id,
            resume_hash,
            headers,
            cookies,
            internal_api_base_url=internal_api_base_url,
            ignore_postponed=ignore_postponed,
            incomplete=incomplete,
            mark_applicant_visible_in_vacancy_country=mark_applicant_visible_in_vacancy_country,
            country_ids=country_ids,
            letter=letter,
            lux=lux,
            without_test=without_test,
            hhtm_from_label=hhtm_from_label,
            hhtm_source_label=hhtm_source_label,
            return_cookies=return_cookies,
        )

    async def fetch_resumes(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        return_cookies: bool = False,
    ) -> List[HHResume] | tuple[List[HHResume], Dict[str, str]]:
        await self._limiter.acquire()
        return await super().fetch_resumes(headers, cookies, internal_api_base_url=internal_api_base_url, return_cookies=return_cookies)

    async def fetch_resume_detail(
        self,
        resume_hash: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        return_cookies: bool = False,
    ) -> Optional[HHResumeDetailed] | tuple[Optional[HHResumeDetailed], Dict[str, str]]:
        await self._limiter.acquire()
        return await super().fetch_resume_detail(resume_hash, headers, cookies, internal_api_base_url=internal_api_base_url, return_cookies=return_cookies)

    async def fetch_chat_list(
        self,
        chat_ids: List[int],
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        chatik_api_base_url: str = "https://chatik.hh.ru",
        return_cookies: bool = False,
    ) -> HHListChat | tuple[HHListChat, Dict[str, str]]:
        await self._limiter.acquire()
        return await super().fetch_chat_list(chat_ids, headers, cookies, chatik_api_base_url=chatik_api_base_url, return_cookies=return_cookies)

    async def fetch_chat_detail(
        self,
        chat_id: int,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        chatik_api_base_url: str = "https://chatik.hh.ru",
        return_cookies: bool = False,
    ) -> Optional[HHChatDetailed] | tuple[Optional[HHChatDetailed], Dict[str, str]]:
        await self._limiter.acquire()
        return await super().fetch_chat_detail(chat_id, headers, cookies, chatik_api_base_url=chatik_api_base_url, return_cookies=return_cookies)

    async def touch_resume(
        self,
        resume_hash: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        undirectable: bool = True,
        return_cookies: bool = False,
    ) -> Dict[str, Any] | tuple[Dict[str, Any], Dict[str, str]]:
        await self._limiter.acquire()
        return await super().touch_resume(
            resume_hash, headers, cookies, internal_api_base_url=internal_api_base_url, undirectable=undirectable, return_cookies=return_cookies
        )
