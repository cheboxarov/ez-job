"""Клиент для работы с резюме HH API."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Union

import httpx
from loguru import logger

from domain.entities.hh_resume import HHResume
from domain.entities.hh_resume_detailed import HHResumeDetailed, HHWorkExperience
from infrastructure.clients.hh_base_mixin import HHBaseMixin


class HHResumeClient(HHBaseMixin):
    """Клиент для работы с резюме в HH API."""

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

        logger.debug(f"[resumes] GET {url}")

        enhanced_headers = self._enhance_headers(headers, cookies)
        async with httpx.AsyncClient(headers=enhanced_headers, cookies=cookies, timeout=self._timeout) as client:
            try:
                resp = await client.get(url)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                logger.error(
                    f"[resumes] HTTP {response.status_code} for {response.request.url}"
                )
                ct = response.headers.get("Content-Type", "")
                logger.debug(f"[resumes] Content-Type: {ct}")
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                logger.debug(f"[resumes] Body preview: {body_preview}")
                raise

            try:
                payload = resp.json()
            except json.JSONDecodeError as exc:
                text = resp.text
                logger.error(
                    f"[resumes] Не удалось распарсить JSON ответа: {exc}; body_len={len(text)}"
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
                logger.warning(f"[resumes] Ошибка маппинга резюме: {exc}")
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

        logger.debug(f"[resume_detail] GET {url} hash={resume_hash}")

        enhanced_headers = self._enhance_headers(headers, cookies)
        async with httpx.AsyncClient(headers=enhanced_headers, cookies=cookies, timeout=self._timeout) as client:
            try:
                resp = await client.get(url)
            except httpx.HTTPError as exc:
                logger.error(f"[resume_detail] hash={resume_hash}: HTTP ошибка {exc}")
                if return_cookies:
                    updated_cookies = self._extract_cookies(client)
                    return None, updated_cookies
                return None

            if resp.status_code != 200:
                logger.warning(
                    f"[resume_detail] hash={resume_hash}: неожиданный статус HTTP {resp.status_code}"
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
                    f"[resume_detail] hash={resume_hash}: ответ не JSON, длина={len(text)}"
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
            logger.warning(f"[resume_detail] hash={resume_hash}: applicantResume отсутствует или не является словарем")
            if return_cookies:
                return None, updated_cookies
            return None

        try:
            result = self._map_resume_detail_view_to_entity(applicant_resume)
            if return_cookies:
                return result, updated_cookies
            return result
        except Exception as exc:
            logger.error(f"[resume_detail] hash={resume_hash}: ошибка маппинга детального резюме: {exc}")
            if return_cookies:
                return None, updated_cookies
            return None

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

        # Извлекаем _xsrf из cookies или headers
        xsrf_token = cookies.get("_xsrf") or headers.get("x-xsrftoken") or headers.get("X-Xsrftoken") or ""

        form_data: Dict[str, Any] = {
            "resume": resume_hash,
            "undirectable": "true" if undirectable else "false",
        }

        enhanced_headers = self._enhance_headers(headers, cookies)
        async with httpx.AsyncClient(headers=enhanced_headers, cookies=cookies, timeout=self._timeout) as client:
            try:
                resp = await client.post(url, data=form_data)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                logger.error(
                    f"[touch] HTTP {response.status_code} for {response.request.url}"
                )
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                logger.debug(f"[touch] Body preview: {body_preview}")
                raise

            try:
                payload = resp.json()
            except json.JSONDecodeError as exc:
                text = resp.text
                logger.error(
                    f"[touch] Не удалось распарсить JSON ответа: {exc}; body_len={len(text)}"
                )
                raise RuntimeError(
                    f"Не удалось распарсить JSON ответа touch: {exc}; body_len={len(text)}"
                ) from exc

            # Извлечь обновленные cookies после запроса
            updated_cookies = self._extract_cookies(client)

        if return_cookies:
            return payload, updated_cookies
        return payload

    async def edit_resume(
        self,
        resume_hash: str,
        experience: List[Dict[str, Any]],
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        hhtm_source: str = "resume_partial_edit",
        return_cookies: bool = False,
    ) -> Dict[str, Any] | tuple[Dict[str, Any], Dict[str, str]]:
        """Редактировать резюме на HeadHunter по /applicant/resume/edit.
        
        Args:
            resume_hash: Hash резюме для редактирования.
            experience: Список объектов опыта работы для обновления.
            headers: HTTP заголовки для запроса.
            cookies: HTTP cookies для запроса.
            internal_api_base_url: Базовый URL внутреннего API HH.
            hhtm_source: Источник запроса (по умолчанию "resume_partial_edit").
            return_cookies: Если True, возвращает tuple (result, updated_cookies).
        
        Returns:
            Dict[str, Any] с результатом редактирования или tuple[Dict[str, Any], Dict[str, str]] если return_cookies=True.
        """
        base_url = internal_api_base_url.rstrip("/")
        url = f"{base_url}/applicant/resume/edit"
        
        params = {
            "resume": resume_hash,
            "hhtmSource": hhtm_source,
        }
        
        payload = {
            "experience": experience,
        }
        
        logger.debug(f"[edit_resume] POST {url} params={params} resume_hash={resume_hash}")
        
        enhanced_headers = self._enhance_headers(headers, cookies)
        enhanced_headers["content-type"] = "application/json"
        enhanced_headers["x-hhtmfrom"] = "resume_view_block"
        enhanced_headers["x-hhtmsource"] = hhtm_source
        
        async with httpx.AsyncClient(headers=enhanced_headers, cookies=cookies, timeout=self._timeout) as client:
            try:
                resp = await client.post(url, params=params, json=payload)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                logger.error(
                    f"[edit_resume] HTTP {response.status_code} for {response.request.url}"
                )
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                logger.debug(f"[edit_resume] Body preview: {body_preview}")
                raise
            
            try:
                result = resp.json()
            except json.JSONDecodeError as exc:
                text = resp.text
                logger.error(
                    f"[edit_resume] Не удалось распарсить JSON ответа: {exc}; body_len={len(text)}"
                )
                raise RuntimeError(
                    f"Не удалось распарсить JSON ответа edit_resume: {exc}; body_len={len(text)}"
                ) from exc
            
            # Извлечь обновленные cookies после запроса
            updated_cookies = self._extract_cookies(client)
        
        if return_cookies:
            return result, updated_cookies
        return result

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
                    logger.warning(f"[resume_detail] Ошибка парсинга опыта работы: {exc}")
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

