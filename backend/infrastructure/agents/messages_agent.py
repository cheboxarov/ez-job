"""LLM-агент для анализа чатов и генерации ответов на вопросы."""

from __future__ import annotations

import json
from typing import List
from uuid import UUID

from openai import AsyncOpenAI
from loguru import logger

from config import OpenAIConfig
from domain.entities.hh_chat_detailed import HHChatDetailed
from domain.entities.agent_action import AgentAction
from datetime import datetime
from uuid import uuid4
from domain.interfaces.messages_agent_service_port import MessagesAgentServicePort
from infrastructure.agents.base_agent import BaseAgent


class MessagesAgent(BaseAgent, MessagesAgentServicePort):
    """LLM-агент для анализа чатов и генерации ответов на вопросы.

    Инкапсулирует промпты и работу с AsyncOpenAI для анализа чатов,
    определения вопросов и генерации ответов.
    """

    AGENT_NAME = "MessagesAgent"

    async def analyze_chats_and_generate_responses(
        self,
        chats: List[HHChatDetailed],
        resume: str,
        user_id: UUID,
        user_parameters: str | None = None,
        resume_hash: str | None = None,
    ) -> List[AgentAction]:
        """Анализирует чаты и генерирует ответы на вопросы.

        Args:
            chats: Список чатов с детальной информацией и сообщениями.
            resume: Текст резюме кандидата для контекста при генерации ответов.
            user_id: ID пользователя, для которого создаются действия.
            user_parameters: Дополнительные параметры пользователя для контекста (опционально).
            resume_hash: Hash резюме, использованного при создании действий (опционально).

        Returns:
            Список действий для отправки сообщений в чаты с вопросами.
        """
        if not chats:
            return []

        prompt = self._build_prompt(chats, resume, user_parameters)
        logger.info(
            f"[{self.AGENT_NAME}] Анализирую {len(chats)} чатов, model={self._config.model}"
        )

        messages = [
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
   b) create_event - когда требуется создать событие (например, когда компания просит выполнить действие вне чата, или когда работодатель ответил на вопрос пользователя)
3. Для send_message: сгенерировать уместный и вежливый ответ на основе резюме кандидата
4. Для create_event: определить тип события (event_type) и создать событие с описанием

Критерии определения типа действия:

send_message - используй когда:
- Есть простой вопрос, на который можно дать краткий ответ прямо в чате
- Вопросы общего характера (например, "Есть ли у вас опыт с Python?")
- НЕ использовать для: запросов на созвон, встречи, собеседования, действий вне чата

Стиль ответа для send_message:
- Пиши по-человечески: дружелюбно, спокойно, без канцелярита и без “роботской” детализации.
- Будь лаконичным: обычно 1–3 коротких предложения. Не превращай ответ в самопрезентацию.
- Отвечай строго на вопрос собеседника. Не пересказывай резюме/вакансию и не добавляй лишние подробности “на всякий случай”.
- Используй детали из резюме только если они реально помогают ответить на вопрос. Если деталь не спрашивали (например, адрес, точные цифры, длинные списки навыков) — не включай её сама.
- Если вопрос неясный или не хватает данных — задай один уточняющий вопрос вместо длинного ответа.
- Обращение делай нейтральным (“Здравствуйте!”), не используй ФИО/отчество и не выдумывай его.
Дополнительно по оформлению текста:
- НЕ используй длинное тире (символ '—') ни в одном месте ответа.
- Если нужно тире, используй только обычный дефис '-'.

ВАЖНО: Для вопросов, предполагающих ответ "да" или "нет", отвечай строго одним словом: "да" или "нет" (без знаков препинания, без дополнительных слов, без вежливых фраз).
Примеры таких вопросов:
- "Есть ли у вас опыт с Python?" → ответ: "да" или "нет"
- "Готовы ли вы к удаленной работе?" → ответ: "да" или "нет"
- "Согласны ли вы на эту зарплату?" → ответ: "да" или "нет"
- "Работали ли вы с FastAPI?" → ответ: "да" или "нет"
Если вопрос требует ответа "да" или "нет", НЕ используй фразы типа "Да, конечно", "Нет, к сожалению", "Да, у меня есть опыт" и т.п. Только одно слово: "да" или "нет".

ИСПОЛЬЗОВАНИЕ ВАРИАНТОВ ОТВЕТОВ (text_buttons):
- Если в сообщении от работодателя указаны варианты ответов (поле "Варианты ответов" в промпте), ОБЯЗАТЕЛЬНО используй один из предложенных вариантов
- Выбирай наиболее подходящий вариант на основе резюме кандидата и контекста вопроса
- Текст ответа должен ТОЧНО совпадать с выбранным вариантом, включая пробелы, регистр и знаки препинания
- Если ни один вариант не подходит идеально, выбери наиболее близкий по смыслу вариант
- ВАЖНО: Если вариантов ответов нет (поле "Варианты ответов" отсутствует в промпте) ИЛИ массив пустой, генерируй ответ самостоятельно как обычно, используя стандартную логику генерации ответов
- Пример: если есть варианты "не работал", "до 6 месяцев", " от 6 мес до 1 года ", "более 1 года" и в резюме указан опыт 2 года, выбери "более 1 года" (точный текст, включая пробелы)

create_event - используй когда:
- Компания просит назначить созвон/встречу/собеседование (например, "В какое время вам удобно созвониться?", "Когда можем встретиться?", "Предлагаем созвон для знакомства")
- Компания просит выполнить действие вне чата HeadHunter (пройти анкету в телеграме, на сайте компании, заполнить форму на внешней платформе и т.д.)
- Последнее сообщение в чате от работодателя (не от пользователя) является ответом на вопрос, который был задан пользователем ранее в диалоге
- Требуется создать событие для отслеживания или напоминания
- Любая ситуация, которая требует создания события с определенным типом

ВАЖНО: Запросы на созвон/встречу/собеседование НЕ должны получать ответ send_message. Для них нужно создавать create_event.

Типы событий (event_type):
- "call_request" - когда компания просит назначить созвон/встречу/собеседование (например, "В какое время вам удобно созвониться?", "Предлагаем созвон для знакомства")
- "external_action_request" - когда компания просит выполнить действие вне чата (пройти анкету в телеграм-боте, на сайте компании, заполнить форму и т.д.)
- "question_answered" - когда последнее сообщение от работодателя является ответом на вопрос, который был задан пользователем ранее в диалоге

Критерии для создания события "question_answered":
- Последнее сообщение в чате от работодателя (помечено как [ОТ РАБОТОДАТЕЛЯ], НЕ [ОТ ПОЛЬЗОВАТЕЛЯ])
- В предыдущих сообщениях есть вопрос от пользователя (помечен как [ОТ ПОЛЬЗОВАТЕЛЯ])
- Сообщение работодателя по смыслу является ответом на вопрос пользователя
- Если последнее сообщение от пользователя - событие НЕ создается
- Анализируй контекст сообщений выше, чтобы определить, есть ли вопрос от пользователя, на который отвечает работодатель

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
  },
  {
    "type": "create_event",
    "data": {
      "dialog_id": 321,
      "event_type": "question_answered",
      "message": "Работодатель ответил на вопрос о возможности удаленной работы: практически нет, только в исключительных случаях"
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
  * "question_answered" - когда работодатель ответил на вопрос пользователя
- message - краткое описание на русском языке, что требуется сделать или куда нас зовут (для create_event). Для "question_answered" укажи краткое описание ответа работодателя на вопрос пользователя

Никакого другого текста, комментариев или форматирования, только JSON-массив.""",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        def parse_func(content: str) -> List[AgentAction]:
            return self._parse_response(content, chats, user_id, resume_hash)

        def validate_func(result: List[AgentAction]) -> bool:
            return not result

        # Формируем контекст для логирования
        context = {
            "use_case": "analyze_chats_and_generate_responses",
            "chat_ids": [chat.id for chat in chats],
            "chat_count": len(chats),
            "resume_hash": resume_hash,
        }

        return await self._call_llm_with_retry(
            messages=messages,
            parse_func=parse_func,
            validate_func=validate_func,
            user_id=user_id,
            context=context,
        )

    def _build_prompt(
        self,
        chats: List[HHChatDetailed],
        resume: str,
        user_parameters: str | None = None,
    ) -> str:
        """Формирует промпт с информацией о чатах и резюме.

        Args:
            chats: Список чатов для анализа.
            resume: Текст резюме кандидата.
            user_parameters: Дополнительные параметры пользователя для контекста (опционально).

        Returns:
            Текстовый промпт для LLM.
        """
        lines: List[str] = []
        lines.append("РЕЗЮМЕ КАНДИДАТА:")
        lines.append(resume.strip())
        lines.append("")
        
        if user_parameters and user_parameters.strip():
            lines.append("ДОПОЛНИТЕЛЬНЫЕ ПАРАМЕТРЫ ПОЛЬЗОВАТЕЛЯ:")
            lines.append(user_parameters.strip())
            lines.append("")
        
        lines.append("=" * 80)
        lines.append("")

        for chat in chats:
            lines.append(f"ЧАТ #{chat.id}")
            lines.append(f"Тип чата: {chat.type}")
            lines.append(f"Создан: {chat.creation_time}")
            if chat.last_activity_time:
                lines.append(f"Последняя активность: {chat.last_activity_time}")
            if chat.current_participant_id:
                lines.append(f"ID текущего пользователя (кандидата): {chat.current_participant_id}")
            lines.append("")

            # Извлекаем последние 5 сообщений
            last_messages = []
            if chat.messages and chat.messages.items:
                last_messages = chat.messages.items[-5:]

            if last_messages:
                lines.append("Последние сообщения:")
                for msg in last_messages:
                    participant = msg.participant_display.name if msg.participant_display else f"Участник {msg.participant_id or '?'}"
                    # Определяем, от кого сообщение: от пользователя или от работодателя
                    is_from_user = (
                        chat.current_participant_id is not None
                        and msg.participant_id is not None
                        and msg.participant_id == chat.current_participant_id
                    )
                    author_label = "[ОТ ПОЛЬЗОВАТЕЛЯ]" if is_from_user else "[ОТ РАБОТОДАТЕЛЯ]"
                    lines.append(f"  {author_label} [ID: {msg.id}] [{msg.creation_time}] {participant}: {msg.text}")
                    # Добавляем варианты ответов, если они есть и не пустые
                    if msg.text_buttons and len(msg.text_buttons) > 0:
                        buttons_text = ", ".join(f'"{btn}"' for btn in msg.text_buttons)
                        lines.append(f"  Варианты ответов: {buttons_text}")
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
        user_id: UUID,
        resume_hash: str | None = None,
    ) -> List[AgentAction]:
        """Парсит JSON ответ от LLM в список действий.

        Args:
            content: JSON-строка с ответом от LLM.
            chats: Список чатов для валидации dialog_id.
            user_id: ID пользователя, для которого создаются действия.
            resume_hash: Hash резюме, использованного при создании действий (опционально).

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
            logger.error(f"[messages_agent] Ошибка парсинга JSON: {exc}")
            logger.debug(f"[messages_agent] Content: {content[:500]}")
            return []

        if not isinstance(data, list):
            logger.warning("[messages_agent] Ответ не является массивом")
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
                logger.warning(f"[messages_agent] Неверный dialog_id: {dialog_id}")
                continue

            if dialog_id not in chat_ids:
                logger.warning(f"[messages_agent] dialog_id {dialog_id} не найден в списке чатов")
                continue

            # Обрабатываем send_message
            if action_type == "send_message":
                message_text = action_data.get("message_text")
                message_to = action_data.get("message_to")

                if not isinstance(message_text, str) or not message_text.strip():
                    logger.warning(f"[messages_agent] Неверный message_text для dialog_id {dialog_id}")
                    continue

                # Валидируем message_to
                if message_to is not None:
                    if not isinstance(message_to, int):
                        logger.warning(f"[messages_agent] Неверный message_to для dialog_id {dialog_id}: {message_to}")
                        continue
                    
                    # Проверяем, что message_to существует в сообщениях чата
                    chat = next((c for c in chats if c.id == dialog_id), None)
                    if chat and chat.messages and chat.messages.items:
                        message_ids = {msg.id for msg in chat.messages.items}
                        if message_to not in message_ids:
                            logger.warning(f"[messages_agent] message_to {message_to} не найден в сообщениях чата {dialog_id}")
                            # Не прерываем выполнение, просто логируем
                    else:
                        logger.warning(f"[messages_agent] Нет сообщений в чате {dialog_id} для проверки message_to")

                action_data_dict = {
                    "dialog_id": dialog_id,
                    "message_text": message_text.strip(),
                    "sended": False,
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
                        user_id=user_id,
                        resume_hash=resume_hash,
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
                    logger.warning(f"[messages_agent] Неверный event_type для dialog_id {dialog_id}")
                    continue

                if not isinstance(message, str) or not message.strip():
                    logger.warning(f"[messages_agent] Неверный message для create_event dialog_id {dialog_id}")
                    continue

                actions.append(
                    AgentAction(
                        id=uuid4(),
                        type=action_type,
                        entity_type="hh_dialog",
                        entity_id=dialog_id,
                        created_by="messages_agent",
                        user_id=user_id,
                        resume_hash=resume_hash,
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
                logger.warning(f"[messages_agent] Неизвестный тип действия: {action_type}")
                continue

        return actions

