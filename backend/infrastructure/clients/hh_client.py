"""Основной HTTP клиент HH API с множественным наследованием специализированных клиентов."""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, Optional, Union

from domain.entities.hh_chat_detailed import HHChatDetailed
from domain.entities.hh_list_chat import HHListChat
from domain.entities.hh_resume import HHResume
from domain.entities.hh_resume_detailed import HHResumeDetailed
from domain.entities.vacancy_detail import VacancyDetail
from domain.entities.vacancy_list import VacancyList
from domain.entities.vacancy_test import VacancyTest
from domain.interfaces.hh_client_port import HHClientPort
from infrastructure.clients.hh_auth_client import HHAuthClient
from infrastructure.clients.hh_chat_client import HHChatClient
from infrastructure.clients.hh_resume_client import HHResumeClient
from infrastructure.clients.hh_vacancy_client import HHVacancyClient


class HHHttpClient(HHVacancyClient, HHResumeClient, HHChatClient, HHAuthClient, HHClientPort):
    """HTTP‑клиент HH для публичного API (https://api.hh.ru).
    
    Объединяет функциональность всех специализированных клиентов через множественное наследование.
    """

    def __init__(self, base_url: str = "https://api.hh.ru", timeout: float = 30.0) -> None:
        # Вызываем __init__ только от первого родителя (HHBaseMixin через HHVacancyClient)
        # Остальные родители также наследуют от HHBaseMixin, но Python MRO обеспечит правильный порядок
        super().__init__(base_url=base_url, timeout=timeout)


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

    По умолчанию: не более 1 запроса/секунду.
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

    async def get_vacancy_test(
        self,
        vacancy_id: int,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        return_cookies: bool = False,
    ) -> Optional[VacancyTest] | tuple[Optional[VacancyTest], Dict[str, str]]:
        await self._limiter.acquire()
        return await super().get_vacancy_test(
            vacancy_id, headers, cookies, internal_api_base_url=internal_api_base_url, return_cookies=return_cookies
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
        test_answers: Dict[str, str | List[str]] | None = None,
        test_metadata: Dict[str, str] | None = None,
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
            test_answers=test_answers,
            test_metadata=test_metadata,
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
        filter_unread: bool = True,
    ) -> HHListChat | tuple[HHListChat, Dict[str, str]]:
        await self._limiter.acquire()
        return await super().fetch_chat_list(chat_ids, headers, cookies, chatik_api_base_url=chatik_api_base_url, return_cookies=return_cookies, filter_unread=filter_unread)

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

    async def send_chat_message(
        self,
        chat_id: int,
        text: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        chatik_api_base_url: str = "https://chatik.hh.ru",
        idempotency_key: Optional[str] = None,
        hhtm_source: str = "app",
        hhtm_source_label: str = "chat",
        return_cookies: bool = False,
    ) -> Dict[str, Any] | tuple[Dict[str, Any], Dict[str, str]]:
        await self._limiter.acquire()
        return await super().send_chat_message(
            chat_id, text, headers, cookies, chatik_api_base_url=chatik_api_base_url, idempotency_key=idempotency_key, hhtm_source=hhtm_source, hhtm_source_label=hhtm_source_label, return_cookies=return_cookies
        )

    async def mark_chat_message_read(
        self,
        chat_id: int,
        message_id: int,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        chatik_api_base_url: str = "https://chatik.hh.ru",
        hhtm_source: str = "app",
        hhtm_source_label: str = "negotiation_list",
        return_cookies: bool = False,
    ) -> Dict[str, Any] | tuple[Dict[str, Any], Dict[str, str]]:
        await self._limiter.acquire()
        return await super().mark_chat_message_read(
            chat_id, message_id, headers, cookies, chatik_api_base_url=chatik_api_base_url, hhtm_source=hhtm_source, hhtm_source_label=hhtm_source_label, return_cookies=return_cookies
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
        await self._limiter.acquire()
        return await super().touch_resume(
            resume_hash, headers, cookies, internal_api_base_url=internal_api_base_url, undirectable=undirectable, return_cookies=return_cookies
        )

    async def generate_otp(
        self,
        phone: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://novosibirsk.hh.ru",
        login_trust_flags: Optional[str] = None,
        return_cookies: bool = False,
    ) -> Dict[str, Any] | tuple[Dict[str, Any], Dict[str, str]]:
        await self._limiter.acquire()
        return await super().generate_otp(
            phone, headers, cookies, internal_api_base_url=internal_api_base_url, login_trust_flags=login_trust_flags, return_cookies=return_cookies
        )

    async def login_by_code(
        self,
        phone: str,
        code: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://novosibirsk.hh.ru",
        backurl: str = "",
        remember: bool = True,
        login_trust_flags: Optional[str] = None,
        return_cookies: bool = False,
    ) -> Dict[str, Any] | tuple[Dict[str, Any], Dict[str, str]]:
        await self._limiter.acquire()
        return await super().login_by_code(
            phone, code, headers, cookies, internal_api_base_url=internal_api_base_url, backurl=backurl, remember=remember, login_trust_flags=login_trust_flags, return_cookies=return_cookies
        )
