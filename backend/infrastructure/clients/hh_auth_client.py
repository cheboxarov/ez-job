"""Клиент для аутентификации в HH API."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional, Union

import httpx

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

        print(f"[generate_otp] POST {url} phone={phone} data={form_data}", flush=True)

        async with httpx.AsyncClient(
            headers=enhanced_headers, cookies=cookies, timeout=self._timeout
        ) as client:
            try:
                resp = await client.post(url, data=form_data)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                print(
                    f"[generate_otp] HTTP {response.status_code} for {response.request.url}",
                    flush=True,
                )
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                print(f"[generate_otp] Body preview: {body_preview}", flush=True)
                raise

            try:
                payload = resp.json()
            except json.JSONDecodeError as exc:
                text = resp.text
                print(
                    f"[generate_otp] Не удалось распарсить JSON ответа: {exc}; body_len={len(text)}",
                    flush=True,
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

        print(f"[login_by_code] POST {url} phone={phone}", flush=True)

        async with httpx.AsyncClient(
            headers=enhanced_headers, cookies=cookies, timeout=self._timeout
        ) as client:
            try:
                resp = await client.post(url, data=form_data)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                print(
                    f"[login_by_code] HTTP {response.status_code} for {response.request.url}",
                    flush=True,
                )
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                print(f"[login_by_code] Body preview: {body_preview}", flush=True)
                raise

            try:
                payload = resp.json()
            except json.JSONDecodeError as exc:
                text = resp.text
                print(
                    f"[login_by_code] Не удалось распарсить JSON ответа: {exc}; body_len={len(text)}",
                    flush=True,
                )
                raise RuntimeError(
                    f"Не удалось распарсить JSON ответа входа по коду: {exc}; body_len={len(text)}"
                ) from exc

            updated_cookies = self._extract_cookies(client)

        if return_cookies:
            return payload, updated_cookies
        return payload

