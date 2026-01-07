"""Клиент для работы с чатами HH API."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import httpx
from loguru import logger

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
from infrastructure.clients.hh_base_mixin import HHBaseMixin


class HHChatClient(HHBaseMixin):
    """Клиент для работы с чатами в HH API."""

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
        """Получить список чатов по /chatik/api/chats."""
        base_url = chatik_api_base_url.rstrip("/")
        url = f"{base_url}/chatik/api/chats"

        # Обязательные заголовки для chatik API
        enhanced_headers = dict(headers)
        enhanced_headers.setdefault("Accept", "application/json")
        enhanced_headers.setdefault("X-Requested-With", "XMLHttpRequest")
        # Анти-бот заголовки и XSRF токен добавляются через _enhance_headers
        enhanced_headers = self._enhance_headers(enhanced_headers, cookies)

        # Формируем параметры запроса
        params: Dict[str, str] = {
            "do_not_track_session_events": "true",
        }
        if filter_unread:
            params["filterUnread"] = "true"
        # Добавляем ids только если список не пустой
        if chat_ids:
            params["ids"] = ",".join(str(chat_id) for chat_id in chat_ids)

        logger.debug(f"[chat_list] GET {url} params={params}")

        async with httpx.AsyncClient(
            headers=enhanced_headers, cookies=cookies, timeout=self._timeout
        ) as client:
            try:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                logger.error(
                    f"[chat_list] HTTP {response.status_code} for {response.request.url}"
                )
                ct = response.headers.get("Content-Type", "")
                logger.debug(f"[chat_list] Content-Type: {ct}")
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                logger.debug(f"[chat_list] Body preview: {body_preview}")
                raise

            try:
                payload = resp.json()
            except json.JSONDecodeError as exc:
                text = resp.text
                logger.error(
                    f"[chat_list] Не удалось распарсить JSON: {exc}; body_len={len(text)}"
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
                logger.warning(f"[chat_list] Ошибка маппинга чата: {exc}")
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
        # Анти-бот заголовки и XSRF токен добавляются через _enhance_headers
        enhanced_headers = self._enhance_headers(enhanced_headers, cookies)

        # Формируем параметры запроса
        params: Dict[str, str] = {
            "chatId": str(chat_id),
            "do_not_track_session_events": "true",
        }

        logger.debug(f"[chat_detail] GET {url} chat_id={chat_id}")

        async with httpx.AsyncClient(
            headers=enhanced_headers, cookies=cookies, timeout=self._timeout
        ) as client:
            try:
                resp = await client.get(url, params=params)
            except httpx.HTTPError as exc:
                logger.error(f"[chat_detail] chat_id={chat_id}: HTTP ошибка {exc}")
                if return_cookies:
                    updated_cookies = self._extract_cookies(client)
                    return None, updated_cookies
                return None

            if resp.status_code != 200:
                logger.warning(
                    f"[chat_detail] chat_id={chat_id}: неожиданный статус HTTP {resp.status_code}"
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
                    f"[chat_detail] chat_id={chat_id}: ответ не JSON, длина={len(text)}"
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
            logger.warning(f"[chat_detail] chat_id={chat_id}: chat отсутствует или не является словарем")
            if return_cookies:
                return None, updated_cookies
            return None

        try:
            result = self._map_chat_detailed(chat_data)
            if return_cookies:
                return result, updated_cookies
            return result
        except Exception as exc:
            logger.error(f"[chat_detail] chat_id={chat_id}: ошибка маппинга детального чата: {exc}")
            if return_cookies:
                return None, updated_cookies
            return None

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
        """Отправить сообщение в чат по /chatik/api/send."""
        base_url = chatik_api_base_url.rstrip("/")
        url = f"{base_url}/chatik/api/send"

        # Генерируем idempotency_key, если не передан
        if idempotency_key is None:
            idempotency_key = str(uuid4())

        # Формируем параметры запроса
        params: Dict[str, str] = {
            "hhtmSourceLabel": hhtm_source_label,
            "hhtmSource": hhtm_source,
        }

        # Формируем JSON тело запроса
        json_data: Dict[str, Any] = {
            "chatId": chat_id,
            "idempotencyKey": idempotency_key,
            "text": text,
        }

        # Обязательные заголовки для chatik API
        enhanced_headers = dict(headers)
        enhanced_headers.setdefault("Accept", "application/json")
        enhanced_headers.setdefault("Content-Type", "application/json")
        enhanced_headers.setdefault("X-Requested-With", "XMLHttpRequest")
        enhanced_headers.setdefault("x-hhtmsource", hhtm_source)
        enhanced_headers.setdefault("x-hhtmsourcelabel", hhtm_source_label)
        # Анти-бот заголовки и XSRF токен добавляются через _enhance_headers
        enhanced_headers = self._enhance_headers(enhanced_headers, cookies)

        logger.debug(f"[send_message] POST {url} chat_id={chat_id} text={text[:50]}...")

        async with httpx.AsyncClient(
            headers=enhanced_headers, cookies=cookies, timeout=self._timeout
        ) as client:
            try:
                resp = await client.post(url, params=params, json=json_data)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                logger.error(
                    f"[send_message] HTTP {response.status_code} for {response.request.url}"
                )
                ct = response.headers.get("Content-Type", "")
                logger.debug(f"[send_message] Content-Type: {ct}")
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                logger.debug(f"[send_message] Body preview: {body_preview}")
                raise

            try:
                payload = resp.json()
            except json.JSONDecodeError as exc:
                text_resp = resp.text
                logger.error(
                    f"[send_message] Не удалось распарсить JSON ответа: {exc}; body_len={len(text_resp)}"
                )
                raise RuntimeError(
                    f"Не удалось распарсить JSON ответа отправки сообщения: {exc}; body_len={len(text_resp)}"
                ) from exc

            # Извлечь обновленные cookies после запроса
            updated_cookies = self._extract_cookies(client)

        if return_cookies:
            return payload, updated_cookies
        return payload

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
        """Пометить сообщение в чате как прочитанное по /chatik/api/mark_read."""
        base_url = chatik_api_base_url.rstrip("/")
        url = f"{base_url}/chatik/api/mark_read"

        # Формируем JSON тело запроса
        json_data: Dict[str, Any] = {
            "chatId": chat_id,
            "messageId": message_id,
        }

        # Обязательные заголовки для chatik API
        enhanced_headers = dict(headers)
        enhanced_headers.setdefault("Accept", "application/json")
        enhanced_headers.setdefault("Content-Type", "application/json")
        enhanced_headers.setdefault("X-Requested-With", "XMLHttpRequest")
        enhanced_headers.setdefault("x-hhtmsource", hhtm_source)
        enhanced_headers.setdefault("x-hhtmsourcelabel", hhtm_source_label)
        # Анти-бот заголовки и XSRF токен добавляются через _enhance_headers
        enhanced_headers = self._enhance_headers(enhanced_headers, cookies)

        logger.debug(
            f"[mark_read] POST {url} chat_id={chat_id} message_id={message_id}"
        )

        async with httpx.AsyncClient(
            headers=enhanced_headers, cookies=cookies, timeout=self._timeout
        ) as client:
            try:
                resp = await client.post(url, json=json_data)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                response = exc.response
                logger.error(
                    f"[mark_read] HTTP {response.status_code} for {response.request.url}"
                )
                ct = response.headers.get("Content-Type", "")
                logger.debug(f"[mark_read] Content-Type: {ct}")
                try:
                    body_preview = response.text[:500]
                except Exception:
                    body_preview = "<unavailable>"
                logger.debug(f"[mark_read] Body preview: {body_preview}")
                raise

            try:
                payload = resp.json()
            except json.JSONDecodeError as exc:
                text_resp = resp.text
                logger.error(
                    f"[mark_read] Не удалось распарсить JSON ответа: {exc}; body_len={len(text_resp)}"
                )
                raise RuntimeError(
                    f"Не удалось распарсить JSON ответа пометки сообщения как прочитанного: {exc}; body_len={len(text_resp)}"
                ) from exc

            # Извлечь обновленные cookies после запроса
            updated_cookies = self._extract_cookies(client)

        if return_cookies:
            return payload, updated_cookies
        return payload

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

        # Извлекаем варианты ответов из actions.text_buttons
        text_buttons = None
        actions_raw = raw.get("actions")
        if isinstance(actions_raw, dict):
            text_buttons_raw = actions_raw.get("text_buttons")
            if isinstance(text_buttons_raw, list) and len(text_buttons_raw) > 0:
                # Преобразуем массив объектов {"text": "..."} в список строк
                text_buttons = []
                for button in text_buttons_raw:
                    if isinstance(button, dict):
                        button_text = button.get("text")
                        if isinstance(button_text, str) and button_text.strip():
                            text_buttons.append(button_text.strip())
                # Если после обработки список пустой, устанавливаем None
                if not text_buttons:
                    text_buttons = None

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
            text_buttons=text_buttons,
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
                last_message = HHChatClient._map_chat_message(last_message_raw)
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
                            message_items.append(HHChatClient._map_chat_message(msg_raw))
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

