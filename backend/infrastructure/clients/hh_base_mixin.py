"""Базовый mixin для HH клиентов с общими методами."""

from __future__ import annotations

from typing import Dict

import httpx


class HHBaseMixin:
    """Базовый mixin с общими методами для всех HH клиентов."""

    def __init__(self, base_url: str = "https://api.hh.ru", timeout: float = 30.0) -> None:
        """Инициализация базового клиента.

        Args:
            base_url: Базовый URL API.
            timeout: Таймаут запросов в секундах.
        """
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def _enhance_headers(self, headers: Dict[str, str], cookies: Dict[str, str] | None = None) -> Dict[str, str]:
        """Добавляет анти-бот заголовки и XSRF токен ко всем запросам.
        
        Args:
            headers: Исходные заголовки.
            cookies: Cookies для извлечения XSRF токена (опционально).
            
        Returns:
            Копия headers с добавленными анти-бот заголовками и XSRF токеном.
        """
        enhanced = dict(headers)
        
        # Базовые заголовки для имитации браузера (если не заданы)
        enhanced.setdefault("accept", "application/json")
        enhanced.setdefault("accept-language", "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7")
        enhanced.setdefault("priority", "u=1, i")
        enhanced.setdefault("sec-ch-ua", '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"')
        enhanced.setdefault("sec-ch-ua-mobile", "?0")
        enhanced.setdefault("sec-ch-ua-platform", '"macOS"')
        enhanced.setdefault("sec-fetch-dest", "empty")
        enhanced.setdefault("sec-fetch-mode", "cors")
        enhanced.setdefault("sec-fetch-site", "same-origin")
        enhanced.setdefault("user-agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36")
        enhanced.setdefault("x-requested-with", "XMLHttpRequest")
        
        # Sentry заголовки
        enhanced.setdefault("baggage", "sentry-trace_id=7f9ca75f39b043cc86030a036e7d67b0,sentry-sample_rand=0.134108,sentry-environment=production,sentry-release=xhh%4025.52.1.4,sentry-public_key=0cc3a09b6698423b8ca47d3478cfccac,sentry-transaction=%2Fsearch%2Fvacancy,sentry-sample_rate=0.001,sentry-sampled=false")
        enhanced.setdefault("sentry-trace", "7f9ca75f39b043cc86030a036e7d67b0-ba46dcd02a073da0-0")
        
        # HH специфичные заголовки
        enhanced.setdefault("x-static-version", "25.52.1.4")
        
        if cookies:
            fgsscgib_value = cookies.get("fgsscgib-w-hh")
            gsscgib_value = cookies.get("gsscgib-w-hh")

            if fgsscgib_value:
                enhanced["x-gib-fgsscgib-w-hh"] = fgsscgib_value
            
            if gsscgib_value:
                enhanced["x-gib-gsscgib-w-hh"] = gsscgib_value
            
            # Добавляем XSRF токен из cookies
            xsrf_token = cookies.get("_xsrf") or headers.get("x-xsrftoken") or headers.get("X-Xsrftoken") or ""
            if xsrf_token:
                enhanced.setdefault("X-Xsrftoken", xsrf_token)
        print(enhanced)
        return enhanced

    def _enhance_headers_for_html(self, headers: Dict[str, str], cookies: Dict[str, str] | None = None) -> Dict[str, str]:
        """Добавляет анти-бот заголовки и XSRF токен для HTML запросов.
        
        Не перезаписывает уже установленные заголовки (используется для навигационных запросов).
        
        Args:
            headers: Исходные заголовки (уже должны содержать специфичные для HTML заголовки).
            cookies: Cookies для извлечения XSRF токена (опционально).
            
        Returns:
            Копия headers с добавленными анти-бот заголовками и XSRF токеном.
        """
        enhanced = dict(headers)
        
        # Добавляем только анти-бот заголовки и XSRF токен, не трогая уже установленные заголовки
        # Sentry заголовки
        enhanced.setdefault("baggage", "sentry-trace_id=7f9ca75f39b043cc86030a036e7d67b0,sentry-sample_rand=0.134108,sentry-environment=production,sentry-release=xhh%4025.52.1.4,sentry-public_key=0cc3a09b6698423b8ca47d3478cfccac,sentry-transaction=%2Fsearch%2Fvacancy,sentry-sample_rate=0.001,sentry-sampled=false")
        enhanced.setdefault("sentry-trace", "7f9ca75f39b043cc86030a036e7d67b0-ba46dcd02a073da0-0")
        
        # HH специфичные заголовки
        enhanced.setdefault("x-static-version", "25.52.1.4")
        
        if cookies:
            fgsscgib_value = cookies.get("fgsscgib-w-hh")
            gsscgib_value = cookies.get("gsscgib-w-hh")

            if fgsscgib_value:
                enhanced["x-gib-fgsscgib-w-hh"] = fgsscgib_value
            
            if gsscgib_value:
                enhanced["x-gib-gsscgib-w-hh"] = gsscgib_value
            
            # Добавляем XSRF токен из cookies
            xsrf_token = cookies.get("_xsrf") or headers.get("x-xsrftoken") or headers.get("X-Xsrftoken") or ""
            if xsrf_token:
                enhanced.setdefault("X-Xsrftoken", xsrf_token)
        
        return enhanced

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

