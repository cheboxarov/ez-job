"""Обертка над HHHttpClient для автоматического сохранения обновленных cookies."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional
from uuid import UUID

from domain.entities.hh_chat_detailed import HHChatDetailed
from domain.entities.hh_list_chat import HHListChat
from domain.entities.hh_resume import HHResume
from domain.entities.hh_resume_detailed import HHResumeDetailed
from domain.entities.vacancy_detail import VacancyDetail
from domain.entities.vacancy_list import VacancyList
from domain.entities.vacancy_test import VacancyTest
from domain.interfaces.hh_client_port import HHClientPort
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase
from loguru import logger


class HHHttpClientWithCookieUpdate(HHClientPort):
    """Обертка над HHHttpClient, которая автоматически сохраняет обновленные cookies.

    После каждого запроса к HH API извлекает обновленные cookies и сохраняет их
    в БД через UpdateUserHhAuthCookiesUseCase.
    
    Использует lock для синхронизации обновления cookies, чтобы избежать race conditions
    при параллельных запросах.
    """

    def __init__(
        self,
        hh_client: HHClientPort,
        user_id: UUID,
        update_cookies_uc: UpdateUserHhAuthCookiesUseCase,
    ) -> None:
        """Инициализация обертки.

        Args:
            hh_client: Базовый HH клиент для выполнения запросов.
            user_id: UUID пользователя, для которого обновляются cookies.
            update_cookies_uc: Use case для обновления cookies в БД.
        """
        self._hh_client = hh_client
        self._user_id = user_id
        self._update_cookies_uc = update_cookies_uc
        self._cookies_lock = asyncio.Lock()

    async def _update_cookies(self, updated_cookies: Dict[str, str]) -> None:
        """Обновить cookies пользователя в БД.

        Args:
            updated_cookies: Обновленные cookies из ответа HH API.
        """
        async with self._cookies_lock:
            try:
                await self._update_cookies_uc.execute(
                    user_id=self._user_id,
                    updated_cookies=updated_cookies,
                )
                logger.debug(
                    f"Updated cookies for user_id={self._user_id}. "
                    f"Cookies keys: {list(updated_cookies.keys())}"
                )
            except Exception as exc:
                # Логируем ошибку, но не прерываем выполнение основного запроса
                logger.warning(
                    f"Failed to update cookies for user_id={self._user_id}: {exc}",
                    exc_info=True,
                )

    async def fetch_vacancy_list(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        query: Dict[str, str],
        *,
        return_cookies: bool = False,
    ) -> VacancyList | tuple[VacancyList, Dict[str, str]]:
        result, updated_cookies = await self._hh_client.fetch_vacancy_list(
            headers, cookies, query, return_cookies=True
        )
        await self._update_cookies(updated_cookies)
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
        result, updated_cookies = await self._hh_client.fetch_vacancy_list_front(
            headers, cookies, query, internal_api_base_url=internal_api_base_url, return_cookies=True
        )
        await self._update_cookies(updated_cookies)
        if return_cookies:
            return result, updated_cookies
        return result

    async def fetch_vacancy_detail(
        self,
        vacancy_id: int,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        return_cookies: bool = False,
    ) -> Optional[VacancyDetail] | tuple[Optional[VacancyDetail], Dict[str, str]]:
        result, updated_cookies = await self._hh_client.fetch_vacancy_detail(
            vacancy_id, headers, cookies, return_cookies=True
        )
        await self._update_cookies(updated_cookies)
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
        result, updated_cookies = await self._hh_client.fetch_areas(
            headers, cookies, return_cookies=True
        )
        await self._update_cookies(updated_cookies)
        if return_cookies:
            return result, updated_cookies
        return result

    async def get_vacancy_test(
        self,
        vacancy_id: int,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        return_cookies: bool = False,
    ) -> Optional[VacancyTest] | tuple[Optional[VacancyTest], Dict[str, str]]:
        result, updated_cookies = await self._hh_client.get_vacancy_test(
            vacancy_id,
            headers,
            cookies,
            internal_api_base_url=internal_api_base_url,
            return_cookies=True,
        )
        await self._update_cookies(updated_cookies)
        if return_cookies:
            return result, updated_cookies
        return result

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
        result, updated_cookies = await self._hh_client.respond_to_vacancy(
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
            return_cookies=True,
        )
        await self._update_cookies(updated_cookies)
        if return_cookies:
            return result, updated_cookies
        return result

    async def fetch_resumes(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        return_cookies: bool = False,
    ) -> List[HHResume] | tuple[List[HHResume], Dict[str, str]]:
        result, updated_cookies = await self._hh_client.fetch_resumes(
            headers, cookies, internal_api_base_url=internal_api_base_url, return_cookies=True
        )
        await self._update_cookies(updated_cookies)
        if return_cookies:
            return result, updated_cookies
        return result

    async def fetch_resume_detail(
        self,
        resume_hash: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        return_cookies: bool = False,
    ) -> Optional[HHResumeDetailed] | tuple[Optional[HHResumeDetailed], Dict[str, str]]:
        result, updated_cookies = await self._hh_client.fetch_resume_detail(
            resume_hash, headers, cookies, internal_api_base_url=internal_api_base_url, return_cookies=True
        )
        await self._update_cookies(updated_cookies)
        if return_cookies:
            return result, updated_cookies
        return result

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
        result, updated_cookies = await self._hh_client.fetch_chat_list(
            chat_ids, headers, cookies, chatik_api_base_url=chatik_api_base_url, return_cookies=True, filter_unread=filter_unread
        )
        await self._update_cookies(updated_cookies)
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
        result, updated_cookies = await self._hh_client.fetch_chat_detail(
            chat_id, headers, cookies, chatik_api_base_url=chatik_api_base_url, return_cookies=True
        )
        await self._update_cookies(updated_cookies)
        if return_cookies:
            return result, updated_cookies
        return result

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
        result, updated_cookies = await self._hh_client.touch_resume(
            resume_hash,
            headers,
            cookies,
            internal_api_base_url=internal_api_base_url,
            undirectable=undirectable,
            return_cookies=True,
        )
        await self._update_cookies(updated_cookies)
        if return_cookies:
            return result, updated_cookies
        return result

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
        result, updated_cookies = await self._hh_client.generate_otp(
            phone,
            headers,
            cookies,
            internal_api_base_url=internal_api_base_url,
            login_trust_flags=login_trust_flags,
            return_cookies=True,
        )
        await self._update_cookies(updated_cookies)
        if return_cookies:
            return result, updated_cookies
        return result

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
        result, updated_cookies = await self._hh_client.login_by_code(
            phone,
            code,
            headers,
            cookies,
            internal_api_base_url=internal_api_base_url,
            backurl=backurl,
            remember=remember,
            login_trust_flags=login_trust_flags,
            return_cookies=True,
        )
        await self._update_cookies(updated_cookies)
        if return_cookies:
            return result, updated_cookies
        return result

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
        result, updated_cookies = await self._hh_client.send_chat_message(
            chat_id,
            text,
            headers,
            cookies,
            chatik_api_base_url=chatik_api_base_url,
            idempotency_key=idempotency_key,
            hhtm_source=hhtm_source,
            hhtm_source_label=hhtm_source_label,
            return_cookies=True,
        )
        await self._update_cookies(updated_cookies)
        if return_cookies:
            return result, updated_cookies
        return result

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
        result, updated_cookies = await self._hh_client.mark_chat_message_read(
            chat_id,
            message_id,
            headers,
            cookies,
            chatik_api_base_url=chatik_api_base_url,
            hhtm_source=hhtm_source,
            hhtm_source_label=hhtm_source_label,
            return_cookies=True,
        )
        await self._update_cookies(updated_cookies)
        if return_cookies:
            return result, updated_cookies
        return result
