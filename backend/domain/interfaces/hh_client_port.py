from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from domain.entities.hh_chat_detailed import HHChatDetailed
from domain.entities.hh_list_chat import HHListChat
from domain.entities.hh_resume import HHResume
from domain.entities.hh_resume_detailed import HHResumeDetailed
from domain.entities.vacancy_detail import VacancyDetail
from domain.entities.vacancy_list import VacancyList
from domain.entities.vacancy_test import VacancyTest


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
    async def get_vacancy_test(
        self,
        vacancy_id: int,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://krasnoyarsk.hh.ru",
        return_cookies: bool = False,
    ) -> Union[Optional[VacancyTest], tuple[Optional[VacancyTest], Dict[str, str]]]:  # pragma: no cover - интерфейс
        """Получить тест вакансии по /applicant/vacancy_response.
        
        Возвращает None, если тест отсутствует или не удалось распарсить HTML.
        
        Args:
            vacancy_id: ID вакансии.
            headers: HTTP заголовки для запроса.
            cookies: HTTP cookies для запроса.
            internal_api_base_url: Базовый URL внутреннего API.
            return_cookies: Если True, возвращает tuple (result, updated_cookies).
        
        Returns:
            Optional[VacancyTest] или tuple[Optional[VacancyTest], Dict[str, str]] если return_cookies=True.
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
        test_answers: Dict[str, str | List[str]] | None = None,
        test_metadata: Dict[str, str] | None = None,
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
            test_answers: Ответы на вопросы теста (ключ - field_name, например "task_291683492_text", значение - ответ).
            test_metadata: Метаданные теста (uidPk, guid, startTime, testRequired).
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
        filter_unread: bool = True,
    ) -> Union[HHListChat, tuple[HHListChat, Dict[str, str]]]:  # pragma: no cover - интерфейс
        """Получить список чатов по /chatik/api/chats.
        
        Args:
            chat_ids: Список ID чатов.
            headers: HTTP заголовки для запроса.
            cookies: HTTP cookies для запроса.
            chatik_api_base_url: Базовый URL Chatik API.
            return_cookies: Если True, возвращает tuple (result, updated_cookies).
            filter_unread: Если True, возвращать только непрочитанные чаты.
        
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

    @abstractmethod
    async def generate_otp(
        self,
        phone: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://hh.ru",
        login_trust_flags: Optional[str] = None,
        return_cookies: bool = False,
        captcha: Optional[Dict[str, str]] = None,
    ) -> Union[Dict[str, Any], tuple[Dict[str, Any], Dict[str, str]]]:  # pragma: no cover - интерфейс
        """Запросить код OTP на телефон по /account/otp_generate.
        
        Args:
            phone: Номер телефона в формате +7XXXXXXXXXX.
            headers: HTTP заголовки для запроса.
            cookies: HTTP cookies для запроса.
            internal_api_base_url: Базовый URL внутреннего API.
            login_trust_flags: Флаги доверия логина.
            return_cookies: Если True, возвращает tuple (result, updated_cookies).
        
        Returns:
            Dict[str, Any] или tuple[Dict[str, Any], Dict[str, str]] если return_cookies=True.
        """

    @abstractmethod
    async def get_captcha_key(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        lang: str = "RU",
        internal_api_base_url: str = "https://hh.ru",
        return_cookies: bool = False,
    ) -> Union[Dict[str, Any], tuple[Dict[str, Any], Dict[str, str]]]:  # pragma: no cover - интерфейс
        """Получить ключ капчи HH через /captcha?lang=RU.

        Args:
            headers: HTTP заголовки для запроса.
            cookies: HTTP cookies для запроса.
            lang: Язык капчи (по умолчанию RU).
            internal_api_base_url: Базовый URL HH.
            return_cookies: Если True, возвращает tuple (result, updated_cookies).

        Returns:
            Dict[str, Any] или tuple[Dict[str, Any], Dict[str, str]] если return_cookies=True.
        """

    @abstractmethod
    async def get_captcha_picture(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        captcha_key: str,
        internal_api_base_url: str = "https://hh.ru",
        return_cookies: bool = False,
    ) -> Union[Dict[str, Any], tuple[Dict[str, Any], Dict[str, str]]]:  # pragma: no cover - интерфейс
        """Получить картинку капчи HH через /captcha/picture?key=...

        Args:
            headers: HTTP заголовки для запроса.
            cookies: HTTP cookies для запроса.
            captcha_key: Ключ капчи.
            internal_api_base_url: Базовый URL HH.
            return_cookies: Если True, возвращает tuple (result, updated_cookies).

        Returns:
            Dict[str, Any] или tuple[Dict[str, Any], Dict[str, str]] если return_cookies=True.
        """

    @abstractmethod
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
    ) -> Union[Dict[str, Any], tuple[Dict[str, Any], Dict[str, str]]]:  # pragma: no cover - интерфейс
        """Войти по коду OTP и получить cookies по /account/login/by_code.
        
        Args:
            phone: Номер телефона в формате +7XXXXXXXXXX.
            code: Код OTP из SMS.
            headers: HTTP заголовки для запроса.
            cookies: HTTP cookies для запроса.
            internal_api_base_url: Базовый URL внутреннего API.
            backurl: URL для редиректа после входа.
            remember: Запомнить пользователя.
            login_trust_flags: Флаги доверия логина.
            return_cookies: Если True, возвращает tuple (result, updated_cookies).
        
        Returns:
            Dict[str, Any] или tuple[Dict[str, Any], Dict[str, str]] если return_cookies=True.
        """

    @abstractmethod
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
    ) -> Union[Dict[str, Any], tuple[Dict[str, Any], Dict[str, str]]]:  # pragma: no cover - интерфейс
        """Отправить сообщение в чат по /chatik/api/send.
        
        Args:
            chat_id: ID чата.
            text: Текст сообщения для отправки.
            headers: HTTP заголовки для запроса.
            cookies: HTTP cookies для запроса.
            chatik_api_base_url: Базовый URL Chatik API.
            idempotency_key: Ключ идемпотентности. Если не указан, будет сгенерирован автоматически.
            hhtm_source: Источник запроса (по умолчанию "app").
            hhtm_source_label: Метка источника (по умолчанию "chat").
            return_cookies: Если True, возвращает tuple (result, updated_cookies).
        
        Returns:
            Dict[str, Any] или tuple[Dict[str, Any], Dict[str, str]] если return_cookies=True.
        """

    @abstractmethod
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
    ) -> Union[Dict[str, Any], tuple[Dict[str, Any], Dict[str, str]]]:  # pragma: no cover - интерфейс
        """Пометить сообщение в чате как прочитанное по /chatik/api/mark_read.
        
        Args:
            chat_id: ID чата.
            message_id: ID сообщения для пометки как прочитанного.
            headers: HTTP заголовки для запроса.
            cookies: HTTP cookies для запроса.
            chatik_api_base_url: Базовый URL Chatik API.
            hhtm_source: Источник запроса (по умолчанию "app").
            hhtm_source_label: Метка источника (по умолчанию "negotiation_list").
            return_cookies: Если True, возвращает tuple (result, updated_cookies).
        
        Returns:
            Dict[str, Any] или tuple[Dict[str, Any], Dict[str, str]] если return_cookies=True.
        """

    @abstractmethod
    async def get_initial_cookies(
        self,
        *,
        backurl: str = "",
        internal_api_base_url: str = "https://hh.ru",
        return_cookies: bool = False,
    ) -> Union[Dict[str, str], tuple[Dict[str, str], Dict[str, str]]]:  # pragma: no cover - интерфейс
        """Получить начальные куки через GET запрос на /account/login?role=applicant&backurl=...
        
        Args:
            backurl: URL для редиректа после входа (опционально).
            internal_api_base_url: Базовый URL внутреннего API HH.
            return_cookies: Если True, возвращает tuple (cookies, updated_cookies).
        
        Returns:
            Dict[str, str] с начальными куки или tuple[Dict[str, str], Dict[str, str]] если return_cookies=True.
        """

