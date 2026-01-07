from __future__ import annotations

import asyncio
from typing import Dict, List

from loguru import logger

from config import AppConfig, load_config
from domain.entities.agent_action import AgentAction
from domain.entities.hh_chat_detailed import HHChatDetailed
from domain.entities.hh_list_chat import HHListChat
from domain.entities.user import User
from domain.entities.user_hh_auth_data import UserHhAuthData
from domain.use_cases.analyze_chats_and_respond import AnalyzeChatsAndRespondUseCase
from domain.use_cases.create_agent_action import CreateAgentActionUseCase
from domain.use_cases.fetch_chats_details import FetchChatsDetailsUseCase
from domain.use_cases.fetch_user_chats import FetchUserChatsUseCase
from domain.use_cases.filter_chats_without_rejection_and_mark_read import (
    FilterChatsWithoutRejectionAndMarkReadUseCase,
)
from domain.use_cases.mark_chat_message_read import MarkChatMessageReadUseCase
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
        self._mark_chat_message_read_uc = MarkChatMessageReadUseCase(self._hh_client)
        self._filter_chats_uc = FilterChatsWithoutRejectionAndMarkReadUseCase(
            mark_chat_message_read_uc=self._mark_chat_message_read_uc
        )

    async def run(self) -> None:
        logger.info("[app] Запускаю получение чатов пользователя...")

        # Создаем UnitOfWork и работаем с БД
        async with UnitOfWork(self._session_factory) as uow:
            # Получаем первого пользователя из БД
            user: User | None = await uow.user_repository.get_first()
            if user is None:
                logger.error("[app] Ошибка: пользователи не найдены в БД")
                return

            logger.info(f"[app] Найден пользователь: {user.id}")

            # Получаем auth данные пользователя
            auth_data: UserHhAuthData | None = await uow.user_hh_auth_data_repository.get_by_user_id(
                user.id
            )
            if auth_data is None:
                logger.error(f"[app] Ошибка: auth данные для пользователя {user.id} не найдены")
                return

            logger.info(f"[app] Получены auth данные для пользователя {user.id}")

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
                logger.info(f"[app] Получено чатов: {len(chat_list.items)}")
            except Exception as exc:
                logger.error(f"[app] Ошибка при получении списка чатов: {exc}", exc_info=True)
                return

            # Фильтруем чаты без отказа и помечаем чаты с отказом как прочитанные
            filtered_chat_list = await self._filter_chats_uc.execute(
                chat_list=chat_list,
                headers=auth_data.headers,
                cookies=auth_data.cookies,
                user_id=user.id,
                update_cookies_uc=update_cookies_uc,
            )
            logger.info(f"[app] Чатов без отказа: {len(filtered_chat_list.items)}")

            # Берем первые 3 чата из отфильтрованного списка (или все, если меньше 3)
            first_chats = filtered_chat_list.items
            if not first_chats:
                logger.warning("[app] Чаты не найдены")
                return

            logger.info(f"[app] Получаю детальную информацию о {len(first_chats)} чатах...")

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
                logger.info(f"[app] Получено детальной информации о чатах: {len(chats_details)}")
            except Exception as exc:
                logger.error(f"[app] Ошибка при получении детальной информации о чатах: {exc}", exc_info=True)
                return

            # Формируем result.txt
            self._generate_result_txt(chats_details, filtered_chat_list)
            logger.info("[app] Запись result.txt завершена")

            # Анализируем чаты и генерируем ответы
            try:
                # Группируем чаты по RESUME из resources
                chats_by_resume: Dict[str, List[HHChatDetailed]] = {}
                chats_without_resume: List[HHChatDetailed] = []

                for chat in chats_details:
                    resume_ids = None
                    if chat.resources and "RESUME" in chat.resources:
                        resume_ids = chat.resources["RESUME"]
                    
                    if resume_ids and len(resume_ids) > 0:
                        # Берем первый RESUME ID (обычно их один)
                        resume_id = resume_ids[0]
                        if resume_id not in chats_by_resume:
                            chats_by_resume[resume_id] = []
                        chats_by_resume[resume_id].append(chat)
                    else:
                        chats_without_resume.append(chat)

                logger.info(f"[app] Чаты сгруппированы: {len(chats_by_resume)} групп по резюме, {len(chats_without_resume)} чатов без резюме")

                # Создаем агента с unit_of_work для логирования
                messages_agent = MessagesAgent(self._config.openai, unit_of_work=uow)

                # Создаем use case
                analyze_chats_uc = AnalyzeChatsAndRespondUseCase(messages_agent)

                all_actions: List[AgentAction] = []

                # Обрабатываем каждую группу чатов с соответствующим резюме
                for resume_id, group_chats in chats_by_resume.items():
                    logger.info(f"[app] Обрабатываю группу из {len(group_chats)} чатов для резюме external_id={resume_id}")
                    
                    # Ищем резюме по external_id
                    resume = await uow.resume_repository.get_by_external_id(
                        external_id=resume_id,
                        user_id=user.id,
                    )
                    
                    if resume is None:
                        logger.warning(f"[app] Резюме с external_id={resume_id} не найдено, пропускаем группу чатов")
                        continue
                    
                    logger.info(f"[app] Используется резюме {resume.id} (external_id={resume_id}) для анализа {len(group_chats)} чатов")

                    # Анализируем чаты этой группы с соответствующим резюме
                    actions = await analyze_chats_uc.execute(
                        chats=group_chats,
                        resume=resume.content,
                        user_id=user.id,
                        user_parameters=resume.user_parameters,
                        resume_hash=resume.headhunter_hash,
                    )
                    
                    all_actions.extend(actions)
                    logger.info(f"[app] Сгенерировано {len(actions)} действий для группы резюме {resume_id}")

                # Обрабатываем чаты без резюме (используем первое доступное резюме или пропускаем)
                if chats_without_resume:
                    logger.info(f"[app] Обрабатываю {len(chats_without_resume)} чатов без резюме")
                    resumes = await uow.resume_repository.list_by_user_id(user.id)
                    if resumes:
                        resume = resumes[0]
                        logger.info(f"[app] Используется первое резюме {resume.id} для чатов без резюме")
                        actions = await analyze_chats_uc.execute(
                            chats=chats_without_resume,
                            resume=resume.content,
                            user_id=user.id,
                            user_parameters=resume.user_parameters,
                            resume_hash=resume.headhunter_hash,
                        )
                        all_actions.extend(actions)
                        logger.info(f"[app] Сгенерировано {len(actions)} действий для чатов без резюме")
                    else:
                        logger.warning("[app] Нет резюме для обработки чатов без резюме, пропускаем")

                logger.info(f"[app] Всего сгенерировано {len(all_actions)} действий для ответов")
                
                # Сохраняем действия в БД
                if all_actions:
                    create_action_uc = CreateAgentActionUseCase(uow.agent_action_repository)
                    saved_count = 0
                    for action in all_actions:
                        try:
                            saved_action = await create_action_uc.execute(action)
                            saved_count += 1
                            dialog_id = action.data.get("dialog_id")
                            if action.type == "send_message":
                                message_text = action.data.get("message_text", "")
                                message_to = action.data.get("message_to")
                                preview = message_text[:100] + "..." if len(message_text) > 100 else message_text
                                message_to_str = f" (ответ на сообщение {message_to})" if message_to else ""
                                logger.info(
                                    f"[app] Сохранено действие: отправить сообщение в чат {dialog_id}{message_to_str}: {preview}"
                                )
                            elif action.type == "create_event":
                                event_type = action.data.get("event_type", "")
                                message = action.data.get("message", "")
                                preview = message[:100] + "..." if len(message) > 100 else message
                                logger.info(
                                    f"[app] Сохранено действие: создать событие в чате {dialog_id}, тип: {event_type}: {preview}"
                                )
                        except Exception as exc:
                            logger.error(f"[app] Ошибка при сохранении действия {action.id}: {exc}", exc_info=True)
                            # Продолжаем сохранять остальные действия
                    
                    logger.info(f"[app] Сохранено {saved_count} из {len(all_actions)} действий в БД")
                else:
                    logger.info("[app] Нет действий для сохранения")

                # Помечаем все чаты, которые были отправлены в агента, как прочитанные
                logger.info(f"[app] Помечаю {len(chats_details)} чатов как прочитанные...")
                mark_read_tasks = []
                for chat in chats_details:
                    # Берем последнее сообщение из чата
                    if chat.messages and chat.messages.items:
                        last_message = chat.messages.items[-1]
                        if last_message and last_message.id:
                            async def mark_read_wrapper(chat_id: int, message_id: int) -> None:
                                try:
                                    await self._mark_chat_message_read_uc.execute(
                                        chat_id=chat_id,
                                        message_id=message_id,
                                        headers=auth_data.headers,
                                        cookies=auth_data.cookies,
                                        user_id=user.id,
                                        update_cookies_uc=update_cookies_uc,
                                    )
                                    logger.debug(f"[app] Успешно помечено как прочитанное: chat_id={chat_id}, message_id={message_id}")
                                except Exception as exc:
                                    logger.error(f"[app] Ошибка при пометке чата {chat_id}, сообщения {message_id} как прочитанного: {exc}")
                            
                            task = asyncio.create_task(mark_read_wrapper(chat.id, last_message.id))
                            mark_read_tasks.append(task)
                        else:
                            logger.warning(f"[app] Не удалось пометить чат {chat.id} как прочитанный: отсутствует last_message или message_id")
                    else:
                        logger.warning(f"[app] Чат {chat.id} не имеет сообщений для пометки как прочитанного")

                if mark_read_tasks:
                    results = await asyncio.gather(*mark_read_tasks, return_exceptions=True)
                    for result in results:
                        if isinstance(result, Exception):
                            logger.error(f"[app] Ошибка при пометке чата как прочитанного: {result}")
                    logger.info(f"[app] Помечено {len([r for r in results if not isinstance(r, Exception)])} из {len(mark_read_tasks)} чатов как прочитанные")
            except Exception as exc:
                logger.error(f"[app] Ошибка при анализе чатов: {exc}", exc_info=True)
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
