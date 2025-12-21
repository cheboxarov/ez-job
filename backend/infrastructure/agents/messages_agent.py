"""LLM-агент для анализа чатов и генерации ответов на вопросы."""

from __future__ import annotations

import json
from typing import List

from openai import AsyncOpenAI

from config import OpenAIConfig
from domain.entities.hh_chat_detailed import HHChatDetailed
from domain.entities.agent_action import AgentAction
from datetime import datetime
from uuid import uuid4
from domain.interfaces.messages_agent_service_port import MessagesAgentServicePort


class MessagesAgent(MessagesAgentServicePort):
    """LLM-агент для анализа чатов и генерации ответов на вопросы.

    Инкапсулирует промпты и работу с AsyncOpenAI для анализа чатов,
    определения вопросов и генерации ответов.
    """

    def __init__(
        self,
        config: OpenAIConfig,
        client: AsyncOpenAI | None = None,
    ) -> None:
        """Инициализация агента.

        Args:
            config: Конфигурация OpenAI.
            client: Опциональный клиент AsyncOpenAI (для тестирования).
        """
        self._config = config
        if client is None:
            api_key = self._config.api_key
            if not api_key:
                raise RuntimeError("OpenAIConfig.api_key не задан (проверь конфиг/окружение)")
            client = AsyncOpenAI(
                base_url=self._config.base_url,
                api_key=api_key,
            )
        self._client = client

    async def analyze_chats_and_generate_responses(
        self,
        chats: List[HHChatDetailed],
        resume: str,
    ) -> List[AgentAction]:
        """Анализирует чаты и генерирует ответы на вопросы.

        Args:
            chats: Список чатов с детальной информацией и сообщениями.
            resume: Текст резюме кандидата для контекста при генерации ответов.

        Returns:
            Список действий для отправки сообщений в чаты с вопросами.
        """
        if not chats:
            return []

        try:
            prompt = self._build_prompt(chats, resume)
            print(
                f"[messages_agent] Анализирую {len(chats)} чатов, model={self._config.model}",
                flush=True,
            )

            response = await self._client.chat.completions.create(
                model=self._config.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Ты ассистент, который анализирует чаты с работодателями и отвечает на вопросы.

Тебе переданы:
- Резюме кандидата (для контекста при ответах)
- Список чатов с последними сообщениями

Твоя задача:
1. Проанализировать каждый чат и определить тип действия, которое требуется
2. Определить два типа действий:
   a) send_message - когда нужно ответить на вопрос в самом чате
   b) create_event - когда требуется создать событие (например, когда компания просит выполнить действие вне чата)
3. Для send_message: сгенерировать уместный и вежливый ответ на основе резюме кандидата
4. Для create_event: определить тип события (event_type) и создать событие с описанием

Критерии определения типа действия:

send_message - используй когда:
- Есть простой вопрос, на который можно дать краткий ответ прямо в чате
- Вопросы общего характера (например, "Есть ли у вас опыт с Python?")
- НЕ использовать для: запросов на созвон, встречи, собеседования, действий вне чата

create_event - используй когда:
- Компания просит назначить созвон/встречу/собеседование (например, "В какое время вам удобно созвониться?", "Когда можем встретиться?", "Предлагаем созвон для знакомства")
- Компания просит выполнить действие вне чата HeadHunter (пройти анкету в телеграме, на сайте компании, заполнить форму на внешней платформе и т.д.)
- Требуется создать событие для отслеживания или напоминания
- Любая ситуация, которая требует создания события с определенным типом

ВАЖНО: Запросы на созвон/встречу/собеседование НЕ должны получать ответ send_message. Для них нужно создавать create_event.

Типы событий (event_type):
- "call_request" - когда компания просит назначить созвон/встречу/собеседование (например, "В какое время вам удобно созвониться?", "Предлагаем созвон для знакомства")
- "external_action_request" - когда компания просит выполнить действие вне чата (пройти анкету в телеграм-боте, на сайте компании, заполнить форму и т.д.)
- В будущем могут быть добавлены другие типы событий

Верни строго JSON-массив объектов вида:
[
  {
    "type": "send_message",
    "data": {
      "dialog_id": 123,
      "message_to": 456,
      "message_text": "Здравствуйте! Да, готов к собеседованию."
    }
  },
  {
    "type": "create_event",
    "data": {
      "dialog_id": 456,
      "event_type": "call_request",
      "message": "Компания предлагает созвон для знакомства, нужно указать удобное время"
    }
  },
  {
    "type": "create_event",
    "data": {
      "dialog_id": 789,
      "event_type": "external_action_request",
      "message": "Компания просит пройти анкету в телеграм-боте @company_bot"
    }
  }
]

Если в чатах нет действий, требующих обработки, верни пустой массив [].

Поля:
- dialog_id - это ID чата (chat.id)
- message_to - ID сообщения, на которое отвечаешь (ОБЯЗАТЕЛЬНО для send_message). Это ID сообщения от собеседника в этом чате, на которое нужно дать ответ. Указывай ID последнего сообщения от собеседника, на которое отвечаешь
- message_text - текст ответа на русском языке (ОБЯЗАТЕЛЬНО для send_message)
- event_type - тип события, строка (для create_event). Используй:
  * "call_request" - для запросов на созвон/встречу/собеседование
  * "external_action_request" - для действий вне чата HH (анкеты, формы и т.д.)
- message - краткое описание на русском языке, что требуется сделать или куда нас зовут (для create_event)

Никакого другого текста, комментариев или форматирования, только JSON-массив.""",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.3,
            )

            content = response.choices[0].message.content if response.choices else None
            if not content:
                print("[messages_agent] Пустой ответ от модели", flush=True)
                return []

            # Логируем превью ответа для диагностики
            preview = content
            print(f"[messages_agent] Raw content preview: {preview}", flush=True)

            return self._parse_response(content, chats)
        except Exception as exc:  # pragma: no cover - диагностический путь
            print(f"[messages_agent] Ошибка при анализе чатов: {exc}", flush=True)
            return []

    def _build_prompt(
        self,
        chats: List[HHChatDetailed],
        resume: str,
    ) -> str:
        """Формирует промпт с информацией о чатах и резюме.

        Args:
            chats: Список чатов для анализа.
            resume: Текст резюме кандидата.

        Returns:
            Текстовый промпт для LLM.
        """
        lines: List[str] = []
        lines.append("РЕЗЮМЕ КАНДИДАТА:")
        lines.append(resume.strip())
        lines.append("")
        lines.append("=" * 80)
        lines.append("")

        for chat in chats:
            lines.append(f"ЧАТ #{chat.id}")
            lines.append(f"Тип чата: {chat.type}")
            lines.append(f"Создан: {chat.creation_time}")
            if chat.last_activity_time:
                lines.append(f"Последняя активность: {chat.last_activity_time}")
            lines.append("")

            # Извлекаем последние 5 сообщений
            last_messages = []
            if chat.messages and chat.messages.items:
                last_messages = chat.messages.items[-5:]

            if last_messages:
                lines.append("Последние сообщения:")
                for msg in last_messages:
                    participant = msg.participant_display.name if msg.participant_display else f"Участник {msg.participant_id or '?'}"
                    lines.append(f"  [ID: {msg.id}] [{msg.creation_time}] {participant}: {msg.text}")
                lines.append("")
            else:
                lines.append("Сообщений нет")
                lines.append("")

            lines.append("-" * 80)
            lines.append("")

        return "\n".join(lines)

    def _parse_response(
        self,
        content: str,
        chats: List[HHChatDetailed],
    ) -> List[AgentAction]:
        """Парсит JSON ответ от LLM в список действий.

        Args:
            content: JSON-строка с ответом от LLM.
            chats: Список чатов для валидации dialog_id.

        Returns:
            Список действий агента.
        """
        try:
            # Извлекаем JSON из ответа (на случай, если есть дополнительные символы)
            content = content.strip()
            # Пытаемся найти JSON массив в тексте
            start_idx = content.find("[")
            end_idx = content.rfind("]") + 1
            if start_idx >= 0 and end_idx > start_idx:
                content = content[start_idx:end_idx]

            data = json.loads(content)
        except json.JSONDecodeError as exc:
            print(f"[messages_agent] Ошибка парсинга JSON: {exc}", flush=True)
            print(f"[messages_agent] Content: {content[:500]}", flush=True)
            return []

        if not isinstance(data, list):
            print("[messages_agent] Ответ не является массивом", flush=True)
            return []

        # Валидируем и создаем действия
        actions: List[AgentAction] = []
        chat_ids = {chat.id for chat in chats}

        for item in data:
            if not isinstance(item, dict):
                continue

            action_type = item.get("type")
            action_data = item.get("data")
            
            if not isinstance(action_data, dict):
                continue

            dialog_id = action_data.get("dialog_id")

            # Валидируем dialog_id
            if not isinstance(dialog_id, int):
                print(f"[messages_agent] Неверный dialog_id: {dialog_id}", flush=True)
                continue

            if dialog_id not in chat_ids:
                print(f"[messages_agent] dialog_id {dialog_id} не найден в списке чатов", flush=True)
                continue

            # Обрабатываем send_message
            if action_type == "send_message":
                message_text = action_data.get("message_text")
                message_to = action_data.get("message_to")

                if not isinstance(message_text, str) or not message_text.strip():
                    print(f"[messages_agent] Неверный message_text для dialog_id {dialog_id}", flush=True)
                    continue

                # Валидируем message_to
                if message_to is not None:
                    if not isinstance(message_to, int):
                        print(f"[messages_agent] Неверный message_to для dialog_id {dialog_id}: {message_to}", flush=True)
                        continue
                    
                    # Проверяем, что message_to существует в сообщениях чата
                    chat = next((c for c in chats if c.id == dialog_id), None)
                    if chat and chat.messages and chat.messages.items:
                        message_ids = {msg.id for msg in chat.messages.items}
                        if message_to not in message_ids:
                            print(f"[messages_agent] message_to {message_to} не найден в сообщениях чата {dialog_id}", flush=True)
                            # Не прерываем выполнение, просто логируем
                    else:
                        print(f"[messages_agent] Нет сообщений в чате {dialog_id} для проверки message_to", flush=True)

                action_data_dict = {
                    "dialog_id": dialog_id,
                    "message_text": message_text.strip(),
                }
                if message_to is not None:
                    action_data_dict["message_to"] = message_to

                actions.append(
                    AgentAction(
                        id=uuid4(),
                        type=action_type,
                        entity_type="hh_dialog",
                        entity_id=dialog_id,
                        created_by="messages_agent",
                        data=action_data_dict,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    )
                )

            # Обрабатываем create_event
            elif action_type == "create_event":
                event_type = action_data.get("event_type")
                message = action_data.get("message")

                if not isinstance(event_type, str) or not event_type.strip():
                    print(f"[messages_agent] Неверный event_type для dialog_id {dialog_id}", flush=True)
                    continue

                if not isinstance(message, str) or not message.strip():
                    print(f"[messages_agent] Неверный message для create_event dialog_id {dialog_id}", flush=True)
                    continue

                actions.append(
                    AgentAction(
                        id=uuid4(),
                        type=action_type,
                        entity_type="hh_dialog",
                        entity_id=dialog_id,
                        created_by="messages_agent",
                        data={
                            "dialog_id": dialog_id,
                            "event_type": event_type.strip(),
                            "message": message.strip(),
                        },
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    )
                )
            else:
                print(f"[messages_agent] Неизвестный тип действия: {action_type}", flush=True)
                continue

        return actions

