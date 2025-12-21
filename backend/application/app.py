from __future__ import annotations

import asyncio
from typing import Dict, List

from config import AppConfig, load_config
from domain.entities.hh_chat_detailed import HHChatDetailed
from domain.entities.hh_list_chat import HHListChat
from domain.entities.user import User
from domain.entities.user_hh_auth_data import UserHhAuthData
from domain.use_cases.analyze_chats_and_respond import AnalyzeChatsAndRespondUseCase
from domain.use_cases.fetch_chats_details import FetchChatsDetailsUseCase
from domain.use_cases.fetch_user_chats import FetchUserChatsUseCase
from domain.use_cases.filter_chats_without_rejection import FilterChatsWithoutRejectionUseCase
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase
from infrastructure.agents.messages_agent import MessagesAgent
from infrastructure.clients.hh_client import HHHttpClient
from infrastructure.database.session import create_session_factory
from infrastructure.database.unit_of_work import UnitOfWork


class Application:
    """Application‑слой: склеивает use case и инфраструктуру и управляет выводом."""

    def __init__(self) -> None:
        # Загружаем общий конфиг приложения
        self._config: AppConfig = load_config()

        # Создаем session_factory для работы с БД
        self._session_factory = create_session_factory(self._config.database)

        # Создаем HH HTTP клиент
        self._hh_client = HHHttpClient(base_url=self._config.hh.base_url)

        # Создаем use cases для работы с чатами
        self._fetch_user_chats_uc = FetchUserChatsUseCase(self._hh_client)
        self._fetch_chats_details_uc = FetchChatsDetailsUseCase(self._hh_client)
        self._filter_chats_uc = FilterChatsWithoutRejectionUseCase()

    async def run(self) -> None:
        print("[app] Запускаю получение чатов пользователя...", flush=True)

        # Создаем UnitOfWork и работаем с БД
        async with UnitOfWork(self._session_factory) as uow:
            # Получаем первого пользователя из БД
            user: User | None = await uow.user_repository.get_first()
            if user is None:
                print("[app] Ошибка: пользователи не найдены в БД", flush=True)
                return

            print(f"[app] Найден пользователь: {user.id}", flush=True)

            # Получаем auth данные пользователя
            auth_data: UserHhAuthData | None = await uow.user_hh_auth_data_repository.get_by_user_id(
                user.id
            )
            if auth_data is None:
                print(f"[app] Ошибка: auth данные для пользователя {user.id} не найдены", flush=True)
                return

            print(f"[app] Получены auth данные для пользователя {user.id}", flush=True)

            # Создаем use case для обновления cookies
            update_cookies_uc = UpdateUserHhAuthCookiesUseCase(
                uow.user_hh_auth_data_repository
            )

            # Получаем список чатов пользователя
            try:
                chat_list: HHListChat = await self._fetch_user_chats_uc.execute(
                    headers=auth_data.headers,
                    cookies=auth_data.cookies,
                    user_id=user.id,
                    update_cookies_uc=update_cookies_uc,
                )
                print(f"[app] Получено чатов: {len(chat_list.items)}", flush=True)
            except Exception as exc:
                print(f"[app] Ошибка при получении списка чатов: {exc}", flush=True)
                return

            # Фильтруем чаты без отказа
            filtered_chat_list = await self._filter_chats_uc.execute(chat_list)
            print(f"[app] Чатов без отказа: {len(filtered_chat_list.items)}", flush=True)

            # Берем первые 3 чата из отфильтрованного списка (или все, если меньше 3)
            first_chats = filtered_chat_list.items
            if not first_chats:
                print("[app] Чаты не найдены", flush=True)
                return

            print(f"[app] Получаю детальную информацию о {len(first_chats)} чатах...", flush=True)

            # Получаем детальную информацию о чатах
            chat_ids = [chat.id for chat in first_chats]
            try:
                chats_details: List[HHChatDetailed] = await self._fetch_chats_details_uc.execute(
                    chat_ids=chat_ids,
                    headers=auth_data.headers,
                    cookies=auth_data.cookies,
                    user_id=user.id,
                    update_cookies_uc=update_cookies_uc,
                )
                print(f"[app] Получено детальной информации о чатах: {len(chats_details)}", flush=True)
            except Exception as exc:
                print(f"[app] Ошибка при получении детальной информации о чатах: {exc}", flush=True)
                return

            # Формируем result.txt
            self._generate_result_txt(chats_details, filtered_chat_list)
            print("[app] Запись result.txt завершена", flush=True)

            # Анализируем чаты и генерируем ответы
            try:
                # Получаем первое резюме пользователя для контекста
                resumes = await uow.resume_repository.list_by_user_id(user.id)
                if not resumes:
                    print("[app] У пользователя нет резюме, пропускаем анализ чатов", flush=True)
                else:
                    resume = resumes[0]
                    print(f"[app] Используется резюме {resume.id} для анализа чатов", flush=True)

                    # Создаем агента
                    messages_agent = MessagesAgent(self._config.openai)

                    # Создаем use case
                    analyze_chats_uc = AnalyzeChatsAndRespondUseCase(messages_agent)

                    # Анализируем чаты и генерируем ответы
                    actions = await analyze_chats_uc.execute(
                        chats=chats_details,
                        resume=resume.content,
                    )

                    print(f"[app] Сгенерировано {len(actions)} действий для ответов", flush=True)
                    for action in actions:
                        dialog_id = action.data.get("dialog_id")
                        if action.type == "send_message":
                            message_text = action.data.get("message_text", "")
                            message_to = action.data.get("message_to")
                            preview = message_text[:100] + "..." if len(message_text) > 100 else message_text
                            message_to_str = f" (ответ на сообщение {message_to})" if message_to else ""
                            print(
                                f"[app] Действие: отправить сообщение в чат {dialog_id}{message_to_str}: {preview}",
                                flush=True,
                            )
                        elif action.type == "create_event":
                            event_type = action.data.get("event_type", "")
                            message = action.data.get("message", "")
                            preview = message[:100] + "..." if len(message) > 100 else message
                            print(
                                f"[app] Действие: создать событие в чате {dialog_id}, тип: {event_type}: {preview}",
                                flush=True,
                            )
            except Exception as exc:
                print(f"[app] Ошибка при анализе чатов: {exc}", flush=True)
                # Не прерываем выполнение, продолжаем работу

    def _generate_result_txt(
        self,
        chats_details: List[HHChatDetailed],
        chat_list: HHListChat,
    ) -> None:
        """Формирует result.txt с информацией о чатах и их сообщениях.

        Args:
            chats_details: Список детальной информации о чатах.
            chat_list: Список чатов с display info.
        """
        lines: List[str] = []
        lines.append("=" * 80)
        lines.append(f"ОТЧЕТ О ЧАТАХ ПОЛЬЗОВАТЕЛЯ")
        lines.append(f"Всего чатов: {len(chats_details)}")
        lines.append("=" * 80)
        lines.append("")

        for chat_detail in chats_details:
            # Получаем display info для чата
            display_info = chat_list.display_info.get(chat_detail.id)

            lines.append("-" * 80)
            lines.append(f"ЧАТ #{chat_detail.id}")
            lines.append("-" * 80)

            # Основная информация о чате
            lines.append(f"Тип: {chat_detail.type}")
            lines.append(f"Непрочитанных сообщений: {chat_detail.unread_count}")
            lines.append(f"Создан: {chat_detail.creation_time}")
            if chat_detail.last_activity_time:
                lines.append(f"Последняя активность: {chat_detail.last_activity_time}")

            # Display info
            if display_info:
                lines.append(f"Название: {display_info.title}")
                if display_info.subtitle:
                    lines.append(f"Подзаголовок: {display_info.subtitle}")
                if display_info.icon:
                    lines.append(f"Иконка: {display_info.icon}")

            # Сообщения
            if chat_detail.messages and chat_detail.messages.items:
                lines.append("")
                lines.append(f"Сообщений в чате: {len(chat_detail.messages.items)}")
                if chat_detail.messages.has_more:
                    lines.append("(есть еще сообщения)")
                lines.append("")

                for message in chat_detail.messages.items:
                    lines.append(f"  [Сообщение #{message.id}]")
                    lines.append(f"  Время: {message.creation_time}")
                    if message.participant_display:
                        participant_name = message.participant_display.name
                        is_bot = " (бот)" if message.participant_display.is_bot else ""
                        lines.append(f"  От: {participant_name}{is_bot}")
                    if message.text:
                        # Обрезаем длинный текст
                        text_preview = message.text[:200] + "..." if len(message.text) > 200 else message.text
                        lines.append(f"  Текст: {text_preview}")
                    if message.workflow_transition:
                        lines.append(
                            f"  Workflow: {message.workflow_transition.applicant_state} "
                            f"(topic_id: {message.workflow_transition.topic_id})"
                        )
                    lines.append("")
            else:
                lines.append("")
                lines.append("Сообщений нет")
                lines.append("")

            lines.append("")

        # Записываем в файл
        with open("result.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


def run_app() -> None:
    app = Application()
    asyncio.run(app.run())
