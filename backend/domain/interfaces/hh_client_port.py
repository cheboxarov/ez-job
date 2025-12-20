from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from domain.entities.hh_chat_detailed import HHChatDetailed
from domain.entities.hh_list_chat import HHListChat
from domain.entities.hh_resume import HHResume
from domain.entities.hh_resume_detailed import HHResumeDetailed
from domain.entities.vacancy_detail import VacancyDetail
from domain.entities.vacancy_list import VacancyList


class HHClientPort(ABC):
    """Доменный порт клиента HH.

    Инфраструктура должна реализовать этот интерфейс.
    """

    @abstractmethod
    async def fetch_vacancy_list(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        query: Dict[str, str],
        *,
        return_cookies: bool = False,
    ) -> Union[VacancyList, tuple[VacancyList, Dict[str, str]]]:  # pragma: no cover - интерфейс
        """Получить список кратких вакансий по публичному API /vacancies.
        
        Args:
            headers: HTTP заголовки для запроса.
            cookies: HTTP cookies для запроса.
            query: Query параметры для запроса.
            return_cookies: Если True, возвращает tuple (result, updated_cookies).
        
        Returns:
            VacancyList или tuple[VacancyList, Dict[str, str]] если return_cookies=True.
        """

    @abstractmethod
    async def fetch_vacancy_list_front(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        query: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        return_cookies: bool = False,
    ) -> Union[VacancyList, tuple[VacancyList, Dict[str, str]]]:  # pragma: no cover - интерфейс
        """Получить список кратких вакансий по внутреннему API /search/vacancy.
        
        Args:
            headers: HTTP заголовки для запроса.
            cookies: HTTP cookies для запроса.
            query: Query параметры для запроса.
            internal_api_base_url: Базовый URL внутреннего API.
            return_cookies: Если True, возвращает tuple (result, updated_cookies).
        
        Returns:
            VacancyList или tuple[VacancyList, Dict[str, str]] если return_cookies=True.
        """

    @abstractmethod
    async def fetch_vacancy_detail(
        self,
        vacancy_id: int,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        return_cookies: bool = False,
    ) -> Union[Optional[VacancyDetail], tuple[Optional[VacancyDetail], Dict[str, str]]]:  # pragma: no cover - интерфейс
        """Получить детальную вакансию по /vacancy/{id}.

        Может вернуть None, если вакансия недоступна или не удалось распарсить ответ.
        
        Args:
            vacancy_id: ID вакансии.
            headers: HTTP заголовки для запроса.
            cookies: HTTP cookies для запроса.
            return_cookies: Если True, возвращает tuple (result, updated_cookies).
        
        Returns:
            Optional[VacancyDetail] или tuple[Optional[VacancyDetail], Dict[str, str]] если return_cookies=True.
        """

    @abstractmethod
    async def fetch_areas(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        return_cookies: bool = False,
    ) -> Union[List[Dict[str, Any]], tuple[List[Dict[str, Any]], Dict[str, str]]]:  # pragma: no cover - интерфейс
        """Получить дерево регионов по /areas.
        
        Args:
            headers: HTTP заголовки для запроса.
            cookies: HTTP cookies для запроса.
            return_cookies: Если True, возвращает tuple (result, updated_cookies).
        
        Returns:
            List[Dict[str, Any]] или tuple[List[Dict[str, Any]], Dict[str, str]] если return_cookies=True.
        """

    @abstractmethod
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
    ) -> Union[Dict[str, Any], tuple[Dict[str, Any], Dict[str, str]]]:  # pragma: no cover - интерфейс
        """Откликнуться на вакансию по /applicant/vacancy_response/popup.
        
        Args:
            vacancy_id: ID вакансии.
            resume_hash: Hash резюме.
            headers: HTTP заголовки для запроса.
            cookies: HTTP cookies для запроса.
            internal_api_base_url: Базовый URL внутреннего API.
            ignore_postponed: Игнорировать отложенные отклики.
            incomplete: Неполный отклик.
            mark_applicant_visible_in_vacancy_country: Показать соискателя в стране вакансии.
            country_ids: Список ID стран.
            letter: Текст сопроводительного письма.
            lux: Использовать премиум функции.
            without_test: Без теста.
            hhtm_from_label: Метка источника.
            hhtm_source_label: Метка источника.
            return_cookies: Если True, возвращает tuple (result, updated_cookies).
        
        Returns:
            Dict[str, Any] или tuple[Dict[str, Any], Dict[str, str]] если return_cookies=True.
        """

    @abstractmethod
    async def fetch_resumes(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        return_cookies: bool = False,
    ) -> Union[List[HHResume], tuple[List[HHResume], Dict[str, str]]]:  # pragma: no cover - интерфейс
        """Получить список резюме пользователя по /applicant/resumes.
        
        Args:
            headers: HTTP заголовки для запроса.
            cookies: HTTP cookies для запроса.
            internal_api_base_url: Базовый URL внутреннего API.
            return_cookies: Если True, возвращает tuple (result, updated_cookies).
        
        Returns:
            List[HHResume] или tuple[List[HHResume], Dict[str, str]] если return_cookies=True.
        """

    @abstractmethod
    async def fetch_resume_detail(
        self,
        resume_hash: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        return_cookies: bool = False,
    ) -> Union[Optional[HHResumeDetailed], tuple[Optional[HHResumeDetailed], Dict[str, str]]]:  # pragma: no cover - интерфейс
        """Получить детальное резюме по /resume/{hash}.
        
        Может вернуть None, если резюме недоступно или не удалось распарсить ответ.
        
        Args:
            resume_hash: Hash резюме.
            headers: HTTP заголовки для запроса.
            cookies: HTTP cookies для запроса.
            internal_api_base_url: Базовый URL внутреннего API.
            return_cookies: Если True, возвращает tuple (result, updated_cookies).
        
        Returns:
            Optional[HHResumeDetailed] или tuple[Optional[HHResumeDetailed], Dict[str, str]] если return_cookies=True.
        """

    @abstractmethod
    async def fetch_chat_list(
        self,
        chat_ids: List[int],
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        chatik_api_base_url: str = "https://chatik.hh.ru",
        return_cookies: bool = False,
    ) -> Union[HHListChat, tuple[HHListChat, Dict[str, str]]]:  # pragma: no cover - интерфейс
        """Получить список чатов по /chatik/api/chats.
        
        Args:
            chat_ids: Список ID чатов.
            headers: HTTP заголовки для запроса.
            cookies: HTTP cookies для запроса.
            chatik_api_base_url: Базовый URL Chatik API.
            return_cookies: Если True, возвращает tuple (result, updated_cookies).
        
        Returns:
            HHListChat или tuple[HHListChat, Dict[str, str]] если return_cookies=True.
        """

    @abstractmethod
    async def fetch_chat_detail(
        self,
        chat_id: int,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        chatik_api_base_url: str = "https://chatik.hh.ru",
        return_cookies: bool = False,
    ) -> Union[Optional[HHChatDetailed], tuple[Optional[HHChatDetailed], Dict[str, str]]]:  # pragma: no cover - интерфейс
        """Получить детальную информацию о чате с сообщениями по /chatik/api/chat_data.
        
        Может вернуть None, если чат недоступен или не удалось распарсить ответ.
        
        Args:
            chat_id: ID чата.
            headers: HTTP заголовки для запроса.
            cookies: HTTP cookies для запроса.
            chatik_api_base_url: Базовый URL Chatik API.
            return_cookies: Если True, возвращает tuple (result, updated_cookies).
        
        Returns:
            Optional[HHChatDetailed] или tuple[Optional[HHChatDetailed], Dict[str, str]] если return_cookies=True.
        """

    @abstractmethod
    async def touch_resume(
        self,
        resume_hash: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        undirectable: bool = True,
        return_cookies: bool = False,
    ) -> Union[Dict[str, Any], tuple[Dict[str, Any], Dict[str, str]]]:  # pragma: no cover - интерфейс
        """Поднять резюме в списке по /applicant/resumes/touch.
        
        Args:
            resume_hash: Hash резюме.
            headers: HTTP заголовки для запроса.
            cookies: HTTP cookies для запроса.
            internal_api_base_url: Базовый URL внутреннего API.
            undirectable: Не перенаправлять.
            return_cookies: Если True, возвращает tuple (result, updated_cookies).
        
        Returns:
            Dict[str, Any] или tuple[Dict[str, Any], Dict[str, str]] если return_cookies=True.
        """

