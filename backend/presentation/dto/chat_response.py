"""DTO для ответов чатов."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from domain.entities.hh_chat_detailed import HHChatDetailed, HHChatMessages
from domain.entities.hh_chat_file import HHChatFile
from domain.entities.hh_chat_message import (
    HHChatMessage,
    HHParticipantDisplay,
    HHWorkflowTransition,
)
from domain.entities.hh_list_chat import HHChatDisplayInfo, HHChatListItem, HHListChat


class WorkflowTransitionResponse(BaseModel):
    """DTO для перехода workflow сообщения."""

    id: int = Field(..., description="ID перехода")
    topic_id: int = Field(..., description="ID темы")
    applicant_state: str = Field(..., description="Состояние кандидата")
    declined_by_applicant: bool = Field(..., description="Отклонено кандидатом")


class ParticipantDisplayResponse(BaseModel):
    """DTO для отображения участника чата."""

    name: str = Field(..., description="Имя участника")
    is_bot: bool = Field(..., description="Является ли ботом")


class ChatFileResponse(BaseModel):
    """DTO для файла в сообщении чата."""

    url: str = Field(..., description="Ссылка на файл")
    title: str = Field(..., description="Название файла")
    content_type: str = Field(..., description="MIME-тип")
    upload_id: str = Field(..., description="ID загрузки файла")

    @classmethod
    def from_entity(cls, chat_file: HHChatFile) -> "ChatFileResponse":
        """Создает DTO из доменной сущности файла."""
        return cls(
            url=chat_file.url,
            title=chat_file.title,
            content_type=chat_file.content_type,
            upload_id=chat_file.upload_id,
        )


class ChatMessageResponse(BaseModel):
    """DTO для сообщения в чате."""

    id: int = Field(..., description="ID сообщения")
    chat_id: int = Field(..., description="ID чата")
    creation_time: str = Field(..., description="Время создания")
    text: str = Field(..., description="Текст сообщения")
    type: str = Field(..., description="Тип сообщения")
    can_edit: bool = Field(..., description="Можно ли редактировать")
    can_delete: bool = Field(..., description="Можно ли удалить")
    only_visible_for_my_type: bool = Field(..., description="Видно только для моего типа")
    has_content: bool = Field(..., description="Есть ли контент")
    hidden: bool = Field(..., description="Скрыто ли сообщение")
    workflow_transition_id: Optional[int] = Field(None, description="ID перехода workflow")
    workflow_transition: Optional[WorkflowTransitionResponse] = Field(
        None, description="Переход workflow"
    )
    participant_display: Optional[ParticipantDisplayResponse] = Field(
        None, description="Информация об участнике"
    )
    participant_id: Optional[str] = Field(None, description="ID участника")
    resources: Optional[Dict[str, List[str]]] = Field(None, description="Ресурсы")
    files: Optional[List[ChatFileResponse]] = Field(None, description="Файлы")

    @classmethod
    def from_entity(cls, message: HHChatMessage) -> "ChatMessageResponse":
        """Создает DTO из доменной сущности сообщения.

        Args:
            message: Доменная сущность HHChatMessage.

        Returns:
            DTO для JSON ответа.
        """
        workflow_transition = None
        if message.workflow_transition:
            workflow_transition = WorkflowTransitionResponse(
                id=message.workflow_transition.id,
                topic_id=message.workflow_transition.topic_id,
                applicant_state=message.workflow_transition.applicant_state,
                declined_by_applicant=message.workflow_transition.declined_by_applicant,
            )

        participant_display = None
        if message.participant_display:
            participant_display = ParticipantDisplayResponse(
                name=message.participant_display.name,
                is_bot=message.participant_display.is_bot,
            )

        files = None
        if message.files:
            files = [ChatFileResponse.from_entity(chat_file) for chat_file in message.files]

        return cls(
            id=message.id,
            chat_id=message.chat_id,
            creation_time=message.creation_time,
            text=message.text,
            type=message.type,
            can_edit=message.can_edit,
            can_delete=message.can_delete,
            only_visible_for_my_type=message.only_visible_for_my_type,
            has_content=message.has_content,
            hidden=message.hidden,
            workflow_transition_id=message.workflow_transition_id,
            workflow_transition=workflow_transition,
            participant_display=participant_display,
            participant_id=message.participant_id,
            resources=message.resources,
            files=files,
        )


class ChatDisplayInfoResponse(BaseModel):
    """DTO для информации об отображении чата."""

    title: str = Field(..., description="Название чата")
    subtitle: Optional[str] = Field(None, description="Подзаголовок")
    icon: Optional[str] = Field(None, description="Иконка")

    @classmethod
    def from_entity(cls, display_info: HHChatDisplayInfo) -> "ChatDisplayInfoResponse":
        """Создает DTO из доменной сущности.

        Args:
            display_info: Доменная сущность HHChatDisplayInfo.

        Returns:
            DTO для JSON ответа.
        """
        return cls(
            title=display_info.title,
            subtitle=display_info.subtitle,
            icon=display_info.icon,
        )


class ChatListItemResponse(BaseModel):
    """DTO для элемента списка чатов."""

    id: int = Field(..., description="ID чата")
    type: str = Field(..., description="Тип чата")
    unread_count: int = Field(..., description="Количество непрочитанных сообщений")
    pinned: bool = Field(..., description="Закреплен ли чат")
    notification_enabled: bool = Field(..., description="Включены ли уведомления")
    creation_time: str = Field(..., description="Время создания")
    idempotency_key: str = Field(..., description="Ключ идемпотентности")
    owner_violates_rules: bool = Field(..., description="Нарушает ли владелец правила")
    untrusted_employer_restrictions_applied: bool = Field(
        ..., description="Применены ли ограничения для ненадежного работодателя"
    )
    current_participant_id: str = Field(..., description="ID текущего участника")
    last_activity_time: Optional[str] = Field(None, description="Время последней активности")
    last_message: Optional[ChatMessageResponse] = Field(None, description="Последнее сообщение")
    last_viewed_by_opponent_message_id: Optional[int] = Field(
        None, description="ID последнего сообщения, просмотренного оппонентом"
    )
    last_viewed_by_current_user_message_id: Optional[int] = Field(
        None, description="ID последнего сообщения, просмотренного текущим пользователем"
    )
    resources: Optional[Dict[str, List[str]]] = Field(None, description="Ресурсы")
    participants_ids: Optional[List[str]] = Field(None, description="ID участников")
    online_until_time: Optional[str] = Field(None, description="Онлайн до времени")
    block_chat_info: Optional[List[Dict[str, Any]]] = Field(
        None, description="Информация о блокировке чата"
    )
    display_info: Optional[ChatDisplayInfoResponse] = Field(
        None, description="Информация для отображения"
    )

    @classmethod
    def from_entity(
        cls, item: HHChatListItem, display_info: Optional[HHChatDisplayInfo] = None
    ) -> "ChatListItemResponse":
        """Создает DTO из доменной сущности элемента списка чатов.

        Args:
            item: Доменная сущность HHChatListItem.
            display_info: Опциональная информация для отображения чата.

        Returns:
            DTO для JSON ответа.
        """
        last_message = None
        if item.last_message:
            last_message = ChatMessageResponse.from_entity(item.last_message)

        display_info_response = None
        if display_info:
            display_info_response = ChatDisplayInfoResponse.from_entity(display_info)

        return cls(
            id=item.id,
            type=item.type,
            unread_count=item.unread_count,
            pinned=item.pinned,
            notification_enabled=item.notification_enabled,
            creation_time=item.creation_time,
            idempotency_key=item.idempotency_key,
            owner_violates_rules=item.owner_violates_rules,
            untrusted_employer_restrictions_applied=item.untrusted_employer_restrictions_applied,
            current_participant_id=item.current_participant_id,
            last_activity_time=item.last_activity_time,
            last_message=last_message,
            last_viewed_by_opponent_message_id=item.last_viewed_by_opponent_message_id,
            last_viewed_by_current_user_message_id=item.last_viewed_by_current_user_message_id,
            resources=item.resources,
            participants_ids=item.participants_ids,
            online_until_time=item.online_until_time,
            block_chat_info=item.block_chat_info,
            display_info=display_info_response,
        )


class ChatListResponse(BaseModel):
    """DTO для ответа со списком чатов."""

    count: int = Field(..., description="Количество чатов")
    items: List[ChatListItemResponse] = Field(..., description="Список чатов")

    @classmethod
    def from_entity(cls, chat_list: HHListChat) -> "ChatListResponse":
        """Создает DTO из доменной сущности списка чатов.

        Args:
            chat_list: Доменная сущность HHListChat.

        Returns:
            DTO для JSON ответа.
        """
        items = []
        for item in chat_list.items:
            display_info = chat_list.display_info.get(item.id)
            items.append(ChatListItemResponse.from_entity(item, display_info))

        return cls(count=len(items), items=items)


class ChatMessagesResponse(BaseModel):
    """DTO для списка сообщений в чате."""

    items: List[ChatMessageResponse] = Field(..., description="Список сообщений")
    has_more: bool = Field(..., description="Есть ли еще сообщения")

    @classmethod
    def from_entity(cls, messages: HHChatMessages) -> "ChatMessagesResponse":
        """Создает DTO из доменной сущности сообщений.

        Args:
            messages: Доменная сущность HHChatMessages.

        Returns:
            DTO для JSON ответа.
        """
        return cls(
            items=[ChatMessageResponse.from_entity(msg) for msg in messages.items],
            has_more=messages.has_more,
        )


class ChatDetailedResponse(BaseModel):
    """DTO для детальной информации о чате."""

    id: int = Field(..., description="ID чата")
    type: str = Field(..., description="Тип чата")
    unread_count: int = Field(..., description="Количество непрочитанных сообщений")
    pinned: bool = Field(..., description="Закреплен ли чат")
    notification_enabled: bool = Field(..., description="Включены ли уведомления")
    creation_time: str = Field(..., description="Время создания")
    owner_violates_rules: bool = Field(..., description="Нарушает ли владелец правила")
    untrusted_employer_restrictions_applied: bool = Field(
        ..., description="Применены ли ограничения для ненадежного работодателя"
    )
    current_participant_id: str = Field(..., description="ID текущего участника")
    last_activity_time: Optional[str] = Field(None, description="Время последней активности")
    messages: Optional[ChatMessagesResponse] = Field(None, description="Сообщения чата")
    last_viewed_by_opponent_message_id: Optional[int] = Field(
        None, description="ID последнего сообщения, просмотренного оппонентом"
    )
    last_viewed_by_current_user_message_id: Optional[int] = Field(
        None, description="ID последнего сообщения, просмотренного текущим пользователем"
    )
    resources: Optional[Dict[str, List[str]]] = Field(None, description="Ресурсы")
    write_possibility: Optional[Dict[str, Any]] = Field(
        None, description="Возможность писать в чат"
    )
    operations: Optional[Dict[str, Any]] = Field(None, description="Операции с чатом")
    participants_ids: Optional[List[str]] = Field(None, description="ID участников")
    online_until_time: Optional[str] = Field(None, description="Онлайн до времени")
    block_chat_info: Optional[List[Dict[str, Any]]] = Field(
        None, description="Информация о блокировке чата"
    )

    @classmethod
    def from_entity(cls, chat: HHChatDetailed) -> "ChatDetailedResponse":
        """Создает DTO из доменной сущности детального чата.

        Args:
            chat: Доменная сущность HHChatDetailed.

        Returns:
            DTO для JSON ответа.
        """
        messages = None
        if chat.messages:
            messages = ChatMessagesResponse.from_entity(chat.messages)

        return cls(
            id=chat.id,
            type=chat.type,
            unread_count=chat.unread_count,
            pinned=chat.pinned,
            notification_enabled=chat.notification_enabled,
            creation_time=chat.creation_time,
            owner_violates_rules=chat.owner_violates_rules,
            untrusted_employer_restrictions_applied=chat.untrusted_employer_restrictions_applied,
            current_participant_id=chat.current_participant_id,
            last_activity_time=chat.last_activity_time,
            messages=messages,
            last_viewed_by_opponent_message_id=chat.last_viewed_by_opponent_message_id,
            last_viewed_by_current_user_message_id=chat.last_viewed_by_current_user_message_id,
            resources=chat.resources,
            write_possibility=chat.write_possibility,
            operations=chat.operations,
            participants_ids=chat.participants_ids,
            online_until_time=chat.online_until_time,
            block_chat_info=chat.block_chat_info,
        )


class SendChatMessageResponse(BaseModel):
    """DTO для ответа отправки сообщения в чат."""

    success: bool = Field(..., description="Успешно ли отправлено сообщение")
    data: Optional[Dict[str, Any]] = Field(None, description="Данные ответа API")
