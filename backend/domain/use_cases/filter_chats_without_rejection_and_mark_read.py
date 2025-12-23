"""Use case для фильтрации чатов без отказа с автоматической пометкой прочитанными чатов с отказом."""

from __future__ import annotations

import asyncio
from typing import Dict, Optional
from uuid import UUID

from loguru import logger

from domain.entities.hh_list_chat import HHListChat
from domain.use_cases.mark_chat_message_read import MarkChatMessageReadUseCase
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase


class FilterChatsWithoutRejectionAndMarkReadUseCase:
    """Use case фильтрации чатов, исключающий чаты с отказом (DISCARD) и помечающий их прочитанными."""

    def __init__(
        self,
        mark_chat_message_read_uc: MarkChatMessageReadUseCase,
    ) -> None:
        """Инициализация use case.

        Args:
            mark_chat_message_read_uc: Use case для пометки сообщения как прочитанного.
        """
        self._mark_chat_message_read_uc = mark_chat_message_read_uc

    async def execute(
        self,
        chat_list: HHListChat,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        *,
        user_id: Optional[UUID] = None,
        update_cookies_uc: Optional[UpdateUserHhAuthCookiesUseCase] = None,
    ) -> HHListChat:
        """Отфильтровать чаты, исключив те, где есть отказ, и пометить чаты с отказом как прочитанные.

        Args:
            chat_list: Список чатов для фильтрации.
            headers: HTTP заголовки для запросов к HH API.
            cookies: HTTP cookies для запросов к HH API.
            user_id: UUID пользователя для обновления cookies (опционально).
            update_cookies_uc: Use case для обновления cookies (опционально).

        Returns:
            Отфильтрованный список чатов без чатов с отказом (DISCARD).
        """
        filtered_items = []
        mark_read_tasks = []

        for item in chat_list.items:
            # Проверяем наличие отказа
            has_rejection = False

            if item.last_message and item.last_message.workflow_transition:
                if item.last_message.workflow_transition.applicant_state == "DISCARD":
                    has_rejection = True

            if has_rejection:
                # Если есть отказ, создаем задачу для пометки прочитанным
                if item.last_message and item.last_message.id:
                    task = self._create_mark_read_task(
                        chat_id=item.id,
                        message_id=item.last_message.id,
                        headers=headers,
                        cookies=cookies,
                        user_id=user_id,
                        update_cookies_uc=update_cookies_uc,
                    )
                    mark_read_tasks.append(task)
                else:
                    logger.warning(
                        f"Не удалось пометить чат {item.id} как прочитанный: "
                        f"отсутствует last_message или message_id"
                    )
            else:
                # Если отказа нет, добавляем чат в отфильтрованный список
                filtered_items.append(item)

        # Выполняем все задачи пометки прочитанным параллельно
        if mark_read_tasks:
            logger.info(
                f"Помечаем {len(mark_read_tasks)} чатов с отказом как прочитанные..."
            )
            results = await asyncio.gather(*mark_read_tasks, return_exceptions=True)
            
            # Обрабатываем результаты и логируем ошибки
            for result in results:
                if isinstance(result, Exception):
                    logger.error(
                        f"Ошибка при пометке чата как прочитанного: {result}",
                        exc_info=result,
                    )

        # Фильтруем display_info, оставляя только записи для оставшихся чатов
        filtered_display_info = {
            chat_id: info
            for chat_id, info in chat_list.display_info.items()
            if chat_id in [item.id for item in filtered_items]
        }

        return HHListChat(items=filtered_items, display_info=filtered_display_info)

    def _create_mark_read_task(
        self,
        chat_id: int,
        message_id: int,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        user_id: Optional[UUID],
        update_cookies_uc: Optional[UpdateUserHhAuthCookiesUseCase],
    ) -> asyncio.Task:
        """Создать задачу для пометки сообщения как прочитанного.

        Args:
            chat_id: ID чата.
            message_id: ID сообщения.
            headers: HTTP заголовки для запросов к HH API.
            cookies: HTTP cookies для запросов к HH API.
            user_id: UUID пользователя для обновления cookies.
            update_cookies_uc: Use case для обновления cookies.

        Returns:
            Задача для асинхронного выполнения.
        """
        async def mark_read_wrapper() -> None:
            try:
                await self._mark_chat_message_read_uc.execute(
                    chat_id=chat_id,
                    message_id=message_id,
                    headers=headers,
                    cookies=cookies,
                    user_id=user_id,
                    update_cookies_uc=update_cookies_uc,
                )
                logger.debug(
                    f"Успешно помечено как прочитанное: chat_id={chat_id}, message_id={message_id}"
                )
            except Exception as exc:
                logger.warning(
                    f"Ошибка при пометке чата {chat_id}, сообщения {message_id} как прочитанного: {exc}",
                    exc_info=exc,
                )
                # Пробрасываем исключение дальше, чтобы asyncio.gather мог его обработать
                raise

        return asyncio.create_task(mark_read_wrapper())

