"""Клиент для аутентификации в HH API."""

from __future__ import annotations

import base64
import json
from typing import Any, Dict, Optional, Union

import httpx
from loguru import logger

from infrastructure.clients.hh_base_mixin import HHBaseMixin


class HHAuthClient(HHBaseMixin):
    """Клиент для аутентификации в HH API."""

    async def generate_otp(
        self,
        phone: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        internal_api_base_url: str = "https://novosibirsk.hh.ru",
        login_trust_flags: Optional[str] = None,
        return_cookies: bool = False,
        captcha: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any] | tuple[Dict[str, Any], Dict[str, str]]:
        """Запросить код OTP на телефон по /account/otp_generate."""
        base_url = internal_api_base_url.rstrip("/")
        url = f"{base_url}/account/otp_generate"

        enhanced_headers = dict(headers)
        enhanced_headers.setdefault("Accept", "application/json")
        enhanced_headers.setdefault("X-Requested-With", "XMLHttpRequest")
        # Анти-бот заголовки и XSRF токен добавляются через _enhance_headers
        enhanced_headers = self._enhance_headers(enhanced_headers, cookies)

        form_data: Dict[str, Any] = {
            "login": phone,
            "otpType": "phone",
            "operationType": "applicant_otp_auth",
            "isSignupPage": "false",
            "captchaText": "",
        }
        
        if login_trust_flags:
            form_data["loginTrustFlags"] = login_trust_flags

        if captcha:
            form_data["captchaKey"] = captcha.get("key", "")
            form_data["captchaText"] = captcha.get("text", "")

        logger.debug(f"[generate_otp] POST {url} phone={phone} data={form_data}")

        async with httpx.AsyncClient(
            headers=enhanced_headers, cookies=cookies, timeout=self._timeout
        ) as client:
            try:
                resp = await client.post(url, data=form_data)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                logger.error(
                    f"[generate_otp] HTTP {response.status_code} for {response.request.url}"
                )
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                logger.debug(f"[generate_otp] Body preview: {body_preview}")
                raise

            try:
                payload = resp.json()
            except json.JSONDecodeError as exc:
                text = resp.text
                logger.error(
                    f"[generate_otp] Не удалось распарсить JSON ответа: {exc}; body_len={len(text)}"
                )
                raise RuntimeError(
                    f"Не удалось распарсить JSON ответа генерации OTP: {exc}; body_len={len(text)}"
                ) from exc

            updated_cookies = self._extract_cookies(client)

        if return_cookies:
            return payload, updated_cookies
        return payload

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
        """Войти по коду OTP и получить cookies по /account/login/by_code."""
        base_url = internal_api_base_url.rstrip("/")
        url = f"{base_url}/account/login/by_code"

        enhanced_headers = dict(headers)
        enhanced_headers.setdefault("Accept", "application/json")
        enhanced_headers.setdefault("X-Requested-With", "XMLHttpRequest")
        # Анти-бот заголовки и XSRF токен добавляются через _enhance_headers
        enhanced_headers = self._enhance_headers(enhanced_headers, cookies)

        if not backurl:
            backurl = f"{base_url}/"

        form_data: Dict[str, Any] = {
            "username": phone,
            "code": code,
            "operationType": "applicant_otp_auth",
            "backurl": backurl,
            "isApplicantSignup": "false",
            "remember": "true" if remember else "false",
        }
        
        if login_trust_flags:
            form_data["loginTrustFlags"] = login_trust_flags

        logger.debug(f"[login_by_code] POST {url} phone={phone}")

        async with httpx.AsyncClient(
            headers=enhanced_headers, cookies=cookies, timeout=self._timeout
        ) as client:
            try:
                resp = await client.post(url, data=form_data)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                logger.error(
                    f"[login_by_code] HTTP {response.status_code} for {response.request.url}"
                )
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                logger.debug(f"[login_by_code] Body preview: {body_preview}")
                raise

            try:
                payload = resp.json()
            except json.JSONDecodeError as exc:
                text = resp.text
                logger.error(
                    f"[login_by_code] Не удалось распарсить JSON ответа: {exc}; body_len={len(text)}"
                )
                raise RuntimeError(
                    f"Не удалось распарсить JSON ответа входа по коду: {exc}; body_len={len(text)}"
                ) from exc

            updated_cookies = self._extract_cookies(client)

        if return_cookies:
            return payload, updated_cookies
        return payload

    async def get_initial_cookies(
        self,
        *,
        backurl: str = "",
        internal_api_base_url: str = "https://hh.ru",
        return_cookies: bool = False,
    ) -> Dict[str, str] | tuple[Dict[str, str], Dict[str, str]]:
        """Получить начальные куки через GET запрос на /account/login?role=applicant&backurl=..."""
        base_url = internal_api_base_url.rstrip("/")
        
        # Формируем URL с параметрами
        params = {"role": "applicant"}
        if backurl:
            params["backurl"] = backurl
        else:
            params["backurl"] = "/"
        
        url = f"{base_url}/account/login"
        
        # Заголовки для HTML запроса (навигационный запрос)
        headers: Dict[str, str] = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "ru-RU,ru;q=0.9",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "referer": f"{base_url}/" if not backurl else f"{base_url}{backurl}",
            "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        }
        
        # Минимальные начальные куки для первого запроса (из curl примера)
        initial_cookies: Dict[str, str] = {
            "gsscgib-w-hh": "i9CAR/HNK8qmYwNpGSdbBRyW5yxR1ukvVdQ4xig+HFJRtMtPSgrudnbHqj6zil+YUqHOUMfItdUFC7+xaJLaYYTf0WFnL5WF7jChKkGIuQWesuAHgLB9Le2yrRf/GErulcXcfX4j0L2Nk99BeN4yE1V9zohJqX/UrwJl6au0OWhXGbB1lESFQMpjjsyiaktaJLG20RnlDUCG8Gtm46ha92F+OgG+ULP0HCin8SNZbHkS8qWQwyZp3II+ZBrvJcCP8w==",
            "cfidsgib-w-hh": "2sH01QNDxauc80H+D479ZLW6ksHQWTGRnuWnonF+HjfiYEzYFX+NdVcjKvd4NzCTeIlmp8dwOa9mtmiNEsEx7BOvLlA9S31wg7WrFrJW6MaLGTQ4Cey2U8Nf72RSGYCKdZuS6j6pYr2SN1uMwdpCO3a4+M+GsUt0Tt4y",
            "fgsscgib-w-hh": "FgC121f47ff0901679063535fd98f84ec9deee93",
            "__zzatgib-w-hh": "MDA0dC0jViV+FmELHw4/aQsbSl1pCENQGC9LXy9ecGlPZ3gSUURcCTIsHRR5aysKf0AVQUFxL1xwIiBoOVURCxIXRF5cVWl1FRpLSiVueCplJS0xViR8SylEXFN/Kh4Wf3IkWAwOVy8NPjteLW8PJwsSWAkhCklpC15MDowIQA==",
        }
        
        # Улучшаем заголовки для HTML запроса
        enhanced_headers = self._enhance_headers_for_html(headers, initial_cookies)
        
        logger.debug(f"[get_initial_cookies] GET {url} params={params}")
        
        async with httpx.AsyncClient(
            headers=enhanced_headers, cookies=initial_cookies, timeout=self._timeout, follow_redirects=True
        ) as client:
            try:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                logger.error(
                    f"[get_initial_cookies] HTTP {response.status_code} for {response.request.url}"
                )
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                logger.debug(f"[get_initial_cookies] Body preview: {body_preview}")
                raise
            
            # Извлекаем куки из ответа
            cookies = self._extract_cookies(client)
        
        if return_cookies:
            return cookies, cookies
        return cookies

    async def get_captcha_key(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        lang: str = "RU",
        internal_api_base_url: str = "https://hh.ru",
        return_cookies: bool = False,
    ) -> Dict[str, Any] | tuple[Dict[str, Any], Dict[str, str]]:
        """Получить ключ капчи HH через /captcha?lang=RU."""
        base_url = internal_api_base_url.rstrip("/")
        url = f"{base_url}/captcha"
        
        params = {"lang": lang}
        
        enhanced_headers = dict(headers)
        enhanced_headers.setdefault("Accept", "application/json")
        enhanced_headers.setdefault("X-Requested-With", "XMLHttpRequest")
        enhanced_headers = self._enhance_headers(enhanced_headers, cookies)
        
        logger.debug(f"[get_captcha_key] GET {url} params={params}")
        
        async with httpx.AsyncClient(
            headers=enhanced_headers, cookies=cookies, timeout=self._timeout
        ) as client:
            try:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                logger.error(
                    f"[get_captcha_key] HTTP {response.status_code} for {response.request.url}"
                )
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                logger.debug(f"[get_captcha_key] Body preview: {body_preview}")
                raise
            
            try:
                payload = resp.json()
            except json.JSONDecodeError as exc:
                text = resp.text
                logger.error(
                    f"[get_captcha_key] Не удалось распарсить JSON ответа: {exc}; body_len={len(text)}"
                )
                raise RuntimeError(
                    f"Не удалось распарсить JSON ответа получения ключа капчи: {exc}; body_len={len(text)}"
                ) from exc
            
            updated_cookies = self._extract_cookies(client)
        
        if return_cookies:
            return payload, updated_cookies
        return payload

    async def get_captcha_picture(
        self,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        captcha_key: str,
        internal_api_base_url: str = "https://hh.ru",
        return_cookies: bool = False,
    ) -> Dict[str, Any] | tuple[Dict[str, Any], Dict[str, str]]:
        """Получить картинку капчи HH через /captcha/picture?key=..."""
        base_url = internal_api_base_url.rstrip("/")
        url = f"{base_url}/captcha/picture"
        
        params = {"key": captcha_key}
        
        enhanced_headers = dict(headers)
        enhanced_headers.setdefault("Accept", "application/json")
        enhanced_headers.setdefault("X-Requested-With", "XMLHttpRequest")
        enhanced_headers = self._enhance_headers(enhanced_headers, cookies)
        
        logger.debug(f"[get_captcha_picture] GET {url} params={params}")
        
        async with httpx.AsyncClient(
            headers=enhanced_headers, cookies=cookies, timeout=self._timeout
        ) as client:
            try:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                logger.error(
                    f"[get_captcha_picture] HTTP {response.status_code} for {response.request.url}"
                )
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                logger.debug(f"[get_captcha_picture] Body preview: {body_preview}")
                raise
            
            # Капча возвращается как изображение
            content_type = resp.headers.get("content-type", "image/png")
            image_bytes = resp.content
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            
            payload = {
                "content_type": content_type,
                "image_base64": image_base64,
            }
            
            updated_cookies = self._extract_cookies(client)
        
        if return_cookies:
            return payload, updated_cookies
        return payload
