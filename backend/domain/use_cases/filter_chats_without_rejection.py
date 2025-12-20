from __future__ import annotations

from domain.entities.hh_list_chat import HHListChat


class FilterChatsWithoutRejectionUseCase:
    """Use case фильтрации чатов, исключающий чаты с отказом (DISCARD)."""

    async def execute(self, chat_list: HHListChat) -> HHListChat:
        """Отфильтровать чаты, исключив те, где есть отказ.

        Args:
            chat_list: Список чатов для фильтрации.

        Returns:
            Отфильтрованный список чатов без чатов с отказом (DISCARD).
        """
        filtered_items = []

        for item in chat_list.items:
            # Проверяем наличие отказа
            has_rejection = False

            if item.last_message and item.last_message.workflow_transition:
                if item.last_message.workflow_transition.applicant_state == "DISCARD":
                    has_rejection = True

            # Если отказа нет, добавляем чат в отфильтрованный список
            if not has_rejection:
                filtered_items.append(item)

        # Фильтруем display_info, оставляя только записи для оставшихся чатов
        filtered_display_info = {
            chat_id: info
            for chat_id, info in chat_list.display_info.items()
            if chat_id in [item.id for item in filtered_items]
        }

        return HHListChat(items=filtered_items, display_info=filtered_display_info)
