"""Клиент для работы с вакансиями HH API."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Union

import httpx
from bs4 import BeautifulSoup
from loguru import logger

from domain.entities.vacancy_detail import VacancyDetail
from domain.entities.vacancy_list import VacancyList, VacancyListItem
from domain.entities.vacancy_test import VacancyTest, VacancyTestQuestion, VacancyTestQuestionOption
from infrastructure.clients.hh_base_mixin import HHBaseMixin


class HHVacancyClient(HHBaseMixin):
    """Клиент для работы с вакансиями в HH API."""

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

        logger.debug(f"[list] GET {url} params={query}")

        enhanced_headers = self._enhance_headers(headers, cookies)
        async with httpx.AsyncClient(headers=enhanced_headers, cookies=cookies, timeout=self._timeout) as client:
            try:
                resp = await client.get(url, params=query)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                logger.error(
                    f"[list] HTTP {response.status_code} for {response.request.url}"
                )
                ct = response.headers.get("Content-Type", "")
                logger.debug(f"[list] Content-Type: {ct}")
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                logger.debug(f"[list] Body preview: {body_preview}")
                raise

            try:
                payload = resp.json()
            except json.JSONDecodeError as exc:  # pragma: no cover - диагностика
                text = resp.text
                logger.error(
                    f"[list] Не удалось распарсить JSON списка вакансий: {exc}; body_len={len(text)}"
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
        # Анти-бот заголовки и XSRF токен добавляются через _enhance_headers
        enhanced_headers = self._enhance_headers(enhanced_headers, cookies)

        # Извлекаем XSRF токен для логирования (если нужен)
        xsrf_token = cookies.get("_xsrf") or enhanced_headers.get("X-Xsrftoken") or ""

        logger.debug(f"[list-front] GET {url} params={query}")
        logger.debug(f"[list-front] Query data: {json.dumps(query, indent=2, ensure_ascii=False)}")
        logger.debug(f"[list-front] Headers keys: {list(enhanced_headers.keys())}")
        logger.debug(f"[list-front] XSRF token: {xsrf_token[:50] if xsrf_token else 'NOT_FOUND'}")

        async with httpx.AsyncClient(
            headers=enhanced_headers, cookies=cookies, timeout=self._timeout
        ) as client:
            try:
                resp = await client.get(url, params=query)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                logger.error(
                    f"[list-front] HTTP {response.status_code} for {response.request.url}"
                )
                ct = response.headers.get("Content-Type", "")
                logger.debug(f"[list-front] Content-Type: {ct}")
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                logger.debug(f"[list-front] Body preview: {body_preview}")
                raise

            try:
                payload = resp.json()
            except json.JSONDecodeError as exc:
                text = resp.text
                logger.error(
                    f"[list-front] Не удалось распарсить JSON: {exc}; body_len={len(text)}"
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

        enhanced_headers = self._enhance_headers(headers, cookies)
        async with httpx.AsyncClient(headers=enhanced_headers, cookies=cookies, timeout=self._timeout) as client:
            try:
                resp = await client.get(url)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                logger.error(
                    f"[areas] HTTP {response.status_code} for {response.request.url}"
                )
                ct = response.headers.get("Content-Type", "")
                logger.debug(f"[areas] Content-Type: {ct}")
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                logger.debug(f"[areas] Body preview: {body_preview}")
                raise

            try:
                payload = resp.json()
            except json.JSONDecodeError as exc:  # pragma: no cover - диагностика
                text = resp.text
                logger.error(
                    f"[areas] Не удалось распарсить JSON дерева регионов: {exc}; body_len={len(text)}"
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

        enhanced_headers = self._enhance_headers(headers, cookies)
        async with httpx.AsyncClient(headers=enhanced_headers, cookies=cookies, timeout=self._timeout) as client:
            try:
                resp = await client.get(url)
            except httpx.HTTPError as exc:  # pragma: no cover - сетевые ошибки
                logger.error(f"[detail] vacancyId={vacancy_id}: HTTP ошибка {exc}")
                if return_cookies:
                    updated_cookies = self._extract_cookies(client)
                    return None, updated_cookies
                return None

            if resp.status_code != 200:
                logger.warning(
                    f"[detail] vacancyId={vacancy_id}: неожиданный статус HTTP {resp.status_code}"
                )
                if return_cookies:
                    updated_cookies = self._extract_cookies(client)
                    return None, updated_cookies
                return None

            try:
                payload = resp.json()
            except json.JSONDecodeError:
                text = resp.text
                logger.error(
                    f"[detail] vacancyId={vacancy_id}: не удалось распарсить JSON; body_len={len(text)}"
                )
                if return_cookies:
                    updated_cookies = self._extract_cookies(client)
                    return None, updated_cookies
                return None

            # Извлечь обновленные cookies после запроса
            updated_cookies = self._extract_cookies(client)

        if not isinstance(payload, dict):
            logger.warning(
                f"[detail] vacancyId={vacancy_id}: ожидался объект в корне ответа"
            )
            if return_cookies:
                return None, updated_cookies
            return None

        try:
            detail = self._map_vacancy_view_to_detail(payload)
        except Exception as exc:
            logger.error(
                f"[detail] vacancyId={vacancy_id}: ошибка маппинга вакансии: {exc}"
            )
            if return_cookies:
                return None, updated_cookies
            return None

        if return_cookies:
            return detail, updated_cookies
        return detail

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

    async def get_vacancy_test(
        self,
        vacancy_id: int,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        return_cookies: bool = False,
    ) -> Optional[VacancyTest] | tuple[Optional[VacancyTest], Dict[str, str]]:
        """Получить тест вакансии по /applicant/vacancy_response."""
        base_url = internal_api_base_url.rstrip("/")
        url = f"{base_url}/applicant/vacancy_response"
        
        params = {"vacancyId": str(vacancy_id)}
        
        # Заголовки для GET запроса HTML страницы (специфичные для навигации)
        get_headers = dict(headers)
        # Устанавливаем заголовки для HTML запроса (перезаписываем, если уже есть)
        get_headers["accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        get_headers["accept-language"] = "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
        get_headers["cache-control"] = "max-age=0"
        get_headers["priority"] = "u=0, i"
        get_headers["sec-ch-ua"] = '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"'
        get_headers["sec-ch-ua-mobile"] = "?0"
        get_headers["sec-ch-ua-platform"] = '"macOS"'
        get_headers["sec-fetch-dest"] = "document"
        get_headers["sec-fetch-mode"] = "navigate"
        get_headers["sec-fetch-site"] = "none"
        get_headers["sec-fetch-user"] = "?1"
        get_headers["upgrade-insecure-requests"] = "1"
        get_headers["user-agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        
        # Добавляем анти-бот заголовки и XSRF токен (но не перезаписываем уже установленные)
        enhanced_headers = self._enhance_headers_for_html(get_headers, cookies)
        
        logger.debug(f"[test] GET {url} vacancyId={vacancy_id}")
        
        async with httpx.AsyncClient(headers=enhanced_headers, cookies=cookies, timeout=self._timeout) as client:
            try:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                logger.error(f"[test] HTTP {exc.response.status_code} for {exc.response.request.url}")
                raise
            
            html_content = resp.text
            updated_cookies = self._extract_cookies(client)
            
            # Парсим HTML через BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Ищем форму с тестом
            form = soup.find('form', {'id': 'RESPONSE_MODAL_FORM_ID'})
            if not form:
                # Тест отсутствует - сохраняем HTML в файл для отладки
                try:
                    from pathlib import Path
                    logs_dir = Path("logs")
                    logs_dir.mkdir(exist_ok=True)
                    html_file = logs_dir / f"{vacancy_id}.html"
                    html_file.write_text(html_content, encoding="utf-8")
                    logger.debug(f"[test] Сохранен HTML в {html_file} для вакансии {vacancy_id}")
                except Exception as save_exc:
                    logger.warning(f"[test] Не удалось сохранить HTML для вакансии {vacancy_id}: {save_exc}")
                
                # Тест отсутствует
                if return_cookies:
                    return None, updated_cookies
                return None
            
            # Извлекаем описание теста
            test_description_elem = soup.find('div', {'data-qa': 'test-description'})
            test_description = test_description_elem.get_text(strip=True) if test_description_elem else None
            
            # Извлекаем метаданные из скрытых полей формы
            uid_pk = None
            guid = None
            start_time = None
            test_required = False
            
            uid_pk_input = form.find('input', {'name': 'uidPk'})
            if uid_pk_input and uid_pk_input.get('value'):
                uid_pk = uid_pk_input['value']
            
            guid_input = form.find('input', {'name': 'guid'})
            if guid_input and guid_input.get('value'):
                guid = guid_input['value']
            
            start_time_input = form.find('input', {'name': 'startTime'})
            if start_time_input and start_time_input.get('value'):
                start_time = start_time_input['value']
            
            test_required_input = form.find('input', {'name': 'testRequired'})
            if test_required_input and test_required_input.get('value'):
                test_required = test_required_input['value'].lower() == 'true'
            
            # Ищем все блоки с вопросами
            questions = []
            task_bodies = form.find_all('div', {'data-qa': 'task-body'})
            
            for task_body in task_bodies:
                # Извлекаем текст вопроса
                question_elem = task_body.find('div', {'data-qa': 'task-question'})
                if not question_elem:
                    continue
                
                question_text = question_elem.get_text(strip=True)
                
                # Проверяем, есть ли textarea (текстовый вопрос)
                textarea = task_body.find('textarea')
                if textarea and textarea.get('name'):
                    # Текстовый вопрос
                    field_name = textarea['name']
                    
                    # Извлекаем task_id из имени поля (например, "task_291683492_text" -> "291683492")
                    match = re.match(r'task_(\d+)_text', field_name)
                    if not match:
                        continue
                    
                    task_id = match.group(1)
                    
                    questions.append(VacancyTestQuestion(
                        task_id=task_id,
                        question_text=question_text,
                        field_name=field_name,
                        question_type="text",
                        options=None,
                    ))
                else:
                    # Проверяем, есть ли checkbox кнопки (multiselect вопрос)
                    checkbox_inputs = task_body.find_all('input', {'type': 'checkbox'})
                    if checkbox_inputs:
                        # Извлекаем name первой checkbox (все должны иметь одинаковый name)
                        first_checkbox = checkbox_inputs[0]
                        field_name = first_checkbox.get('name')
                        if not field_name:
                            continue
                        
                        # Извлекаем task_id из имени поля (например, "task_316925806" -> "316925806")
                        match = re.match(r'task_(\d+)', field_name)
                        if not match:
                            continue
                        
                        task_id = match.group(1)
                        
                        # Извлекаем варианты ответов
                        options = []
                        for checkbox_input in checkbox_inputs:
                            value = checkbox_input.get('value')
                            if not value:
                                continue
                            
                            # Ищем текст варианта ответа
                            # Checkbox находится в label, текст в span с data-qa="cell-text-content"
                            label = checkbox_input.find_parent('label')
                            if label:
                                text_elem = label.find('span', {'data-qa': 'cell-text-content'})
                                if text_elem:
                                    option_text = text_elem.get_text(strip=True)
                                    options.append(VacancyTestQuestionOption(
                                        value=value,
                                        text=option_text,
                                    ))
                        
                        if options:
                            questions.append(VacancyTestQuestion(
                                task_id=task_id,
                                question_text=question_text,
                                field_name=field_name,
                                question_type="multiselect",
                                options=options,
                            ))
                    else:
                        # Проверяем, есть ли radio кнопки (select вопрос)
                        radio_inputs = task_body.find_all('input', {'type': 'radio'})
                        if radio_inputs:
                            # Извлекаем name первой radio кнопки (все должны иметь одинаковый name)
                            first_radio = radio_inputs[0]
                            field_name = first_radio.get('name')
                            if not field_name:
                                continue
                            
                            # Извлекаем task_id из имени поля (например, "task_296586238" -> "296586238")
                            match = re.match(r'task_(\d+)', field_name)
                            if not match:
                                continue
                            
                            task_id = match.group(1)
                            
                            # Извлекаем варианты ответов
                            options = []
                            for radio_input in radio_inputs:
                                value = radio_input.get('value')
                                if not value:
                                    continue
                                
                                # Ищем текст варианта ответа
                                # Radio кнопка находится в label, текст в span с data-qa="cell-text-content"
                                label = radio_input.find_parent('label')
                                if label:
                                    text_elem = label.find('span', {'data-qa': 'cell-text-content'})
                                    if text_elem:
                                        option_text = text_elem.get_text(strip=True)
                                        options.append(VacancyTestQuestionOption(
                                            value=value,
                                            text=option_text,
                                        ))
                            
                            if options:
                                questions.append(VacancyTestQuestion(
                                    task_id=task_id,
                                    question_text=question_text,
                                    field_name=field_name,
                                    question_type="select",
                                    options=options,
                                ))
            
            if not questions:
                # Вопросы не найдены - сохраняем HTML в файл для отладки
                try:
                    from pathlib import Path
                    logs_dir = Path("logs")
                    logs_dir.mkdir(exist_ok=True)
                    html_file = logs_dir / f"{vacancy_id}.html"
                    html_file.write_text(html_content, encoding="utf-8")
                    logger.debug(f"[test] Сохранен HTML в {html_file} для вакансии {vacancy_id} (вопросы не найдены)")
                except Exception as save_exc:
                    logger.warning(f"[test] Не удалось сохранить HTML для вакансии {vacancy_id}: {save_exc}")
                
                # Вопросы не найдены
                if return_cookies:
                    return None, updated_cookies
                return None
            
            test = VacancyTest(
                questions=questions,
                uid_pk=uid_pk,
                guid=guid,
                start_time=start_time,
                test_required=test_required,
                description=test_description,
            )
            
            if return_cookies:
                return test, updated_cookies
            return test

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
        test_answers: Dict[str, str | List[str]] | None = None,
        test_metadata: Dict[str, str] | None = None,
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
        
        # Добавляем метаданные теста, если переданы
        if test_metadata:
            if "uidPk" in test_metadata:
                form_data["uidPk"] = test_metadata["uidPk"]
            if "guid" in test_metadata:
                form_data["guid"] = test_metadata["guid"]
            if "startTime" in test_metadata:
                form_data["startTime"] = test_metadata["startTime"]
            if "testRequired" in test_metadata:
                form_data["testRequired"] = test_metadata["testRequired"]
        
        # Добавляем ответы на вопросы теста, если переданы
        # Для multiselect нужно создать несколько полей с одним именем
        # Используем files параметр со списком кортежей для поддержки multipart/form-data с дублирующимися ключами
        # Формат элемента списка: (key, (filename, value)) -> (key, (None, value)) для текстовых полей
        files_list: List[tuple[str, tuple[None, str]]] = []
        
        # Преобразуем все поля form_data в формат files (список кортежей)
        for key, value in form_data.items():
            files_list.append((key, (None, str(value))))
        
        # Добавляем ответы на вопросы теста
        if test_answers:
            for field_name, answer in test_answers.items():
                if isinstance(answer, list):
                    # Для multiselect - создаем отдельные записи для каждого значения
                    for v in answer:
                        files_list.append((field_name, (None, str(v))))
                else:
                    # Для обычных вопросов - одно поле
                    files_list.append((field_name, (None, str(answer))))

        logger.debug(f"[respond] POST {url} vacancy_id={vacancy_id} resume_hash={resume_hash}")
        # Логируем ключи для отладки
        logger.debug(f"[respond] Form data keys: {[k for k, _ in files_list]}")
        logger.debug(f"[respond] Headers keys: {list(headers.keys())}")
        logger.debug(f"[respond] Cookies keys: {list(cookies.keys())}")
        logger.debug(f"[respond] XSRF token: {xsrf_token[:50] if xsrf_token else 'NOT_FOUND'}")

        enhanced_headers = self._enhance_headers(headers, cookies)
        async with httpx.AsyncClient(headers=enhanced_headers, cookies=cookies, timeout=self._timeout) as client:
            try:
                resp = await client.post(url, files=files_list)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                logger.error(
                    f"[respond] HTTP {response.status_code} for {response.request.url}"
                )
                ct = response.headers.get("Content-Type", "")
                logger.debug(f"[respond] Content-Type: {ct}")
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                logger.debug(f"[respond] Body preview: {body_preview}")
                raise

            try:
                payload = resp.json()
            except json.JSONDecodeError as exc:
                text = resp.text
                logger.error(
                    f"[respond] Не удалось распарсить JSON ответа: {exc}; body_len={len(text)}"
                )
                raise RuntimeError(
                    f"Не удалось распарсить JSON ответа отклика: {exc}; body_len={len(text)}"
                ) from exc

            # Извлечь обновленные cookies после запроса
            updated_cookies = self._extract_cookies(client)

        if return_cookies:
            return payload, updated_cookies
        return payload

