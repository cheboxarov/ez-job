"""Воркер для анализа чатов и создания действий агента."""

from __future__ import annotations

import asyncio
import signal
import sys
from pathlib import Path
from typing import Dict, List

from loguru import logger

# Добавляем корневую директорию проекта в путь
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from config import AppConfig, load_config
from domain.entities.agent_action import AgentAction
from domain.entities.hh_chat_detailed import HHChatDetailed
from domain.entities.hh_list_chat import HHListChat
from domain.use_cases.analyze_chats_and_respond import AnalyzeChatsAndRespondUseCase
from domain.use_cases.create_agent_action import CreateAgentActionUseCase
from domain.use_cases.create_agent_action_with_notification import (
    CreateAgentActionWithNotificationUseCase,
)
from domain.use_cases.fetch_chats_details import FetchChatsDetailsUseCase
from domain.use_cases.fetch_user_chats import FetchUserChatsUseCase
from domain.use_cases.filter_chats_without_rejection_and_mark_read import (
    FilterChatsWithoutRejectionAndMarkReadUseCase,
)
from domain.use_cases.mark_chat_message_read import MarkChatMessageReadUseCase
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase
from domain.use_cases.get_user_automation_settings import GetUserAutomationSettingsUseCase
from domain.use_cases.execute_agent_action import ExecuteAgentActionUseCase
from domain.use_cases.send_chat_message import SendChatMessageUseCase
from domain.use_cases.mark_agent_action_as_sent import MarkAgentActionAsSentUseCase
from infrastructure.agents.messages_agent import MessagesAgent
from infrastructure.clients.hh_client import HHHttpClient
from infrastructure.database.session import create_session_factory
from infrastructure.database.unit_of_work import UnitOfWork

# Настройка loguru
logger.add(
    "logs/chat_analysis_worker_{time}.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    enqueue=True,  # Для асинхронной записи
)

# Флаг для корректного завершения (используется только при запуске как отдельного процесса)
shutdown_event = asyncio.Event()


def setup_signal_handlers(loop: asyncio.AbstractEventLoop, shutdown_event: asyncio.Event) -> None:
    """Настройка обработчиков сигналов для корректного завершения."""
    def signal_handler(signum: int) -> None:
        """Обработчик сигналов для корректного завершения."""
        logger.info(f"Получен сигнал {signum}, завершаем работу...")
        shutdown_event.set()
    
    # Используем add_signal_handler для правильной работы с asyncio
    if sys.platform != "win32":
        loop.add_signal_handler(signal.SIGINT, signal_handler, signal.SIGINT)
        loop.add_signal_handler(signal.SIGTERM, signal_handler, signal.SIGTERM)
    else:
        # На Windows используем signal.signal
        signal.signal(signal.SIGINT, lambda s, f: signal_handler(s))
        signal.signal(signal.SIGTERM, lambda s, f: signal_handler(s))


async def process_chats_cycle(config: AppConfig) -> None:
    """Один цикл обработки чатов.
    
    Args:
        config: Конфигурация приложения.
    """
    session_factory = create_session_factory(config.database)
    hh_client = HHHttpClient(base_url=config.hh.base_url)
    
    # Создаем use cases для работы с чатами
    fetch_user_chats_uc = FetchUserChatsUseCase(hh_client)
    fetch_chats_details_uc = FetchChatsDetailsUseCase(hh_client)
    mark_chat_message_read_uc = MarkChatMessageReadUseCase(hh_client)
    filter_chats_uc = FilterChatsWithoutRejectionAndMarkReadUseCase(
        mark_chat_message_read_uc=mark_chat_message_read_uc
    )
    
    async with UnitOfWork(session_factory) as uow:
        # Создаем агента и use case для анализа с unit_of_work для логирования
        messages_agent = MessagesAgent(config.openai, unit_of_work=uow)
        analyze_chats_uc = AnalyzeChatsAndRespondUseCase(messages_agent)
        # Получаем всех пользователей из БД
        users = await uow.user_repository.list_all()
        
        if not users:
            logger.warning("Пользователи не найдены в БД, пропускаем цикл")
            return
        
        logger.info(f"Найдено пользователей: {len(users)}")
        
        # Обрабатываем каждого пользователя
        for user in users:
            logger.info(f"Обработка чатов для пользователя: {user.id}")
            
            # Получаем auth данные пользователя
            auth_data = await uow.user_hh_auth_data_repository.get_by_user_id(user.id)
            
            if auth_data is None:
                logger.warning(f"Auth данные для пользователя {user.id} не найдены, пропускаем пользователя")
                continue
            
            logger.info(f"Получены auth данные для пользователя {user.id}")
            
            # Создаем use case для обновления cookies
            update_cookies_uc = UpdateUserHhAuthCookiesUseCase(
                uow.standalone_user_hh_auth_data_repository
            )
            
            # Получаем список чатов пользователя
            try:
                chat_list: HHListChat = await fetch_user_chats_uc.execute(
                    headers=auth_data.headers,
                    cookies=auth_data.cookies,
                    user_id=user.id,
                    update_cookies_uc=update_cookies_uc,
                )
                
                logger.info(f"Получено чатов: {len(chat_list.items)}")
            except Exception as exc:
                logger.error(f"Ошибка при получении списка чатов для пользователя {user.id}: {exc}", exc_info=True)
                continue
            
            # Фильтруем чаты без отказа и помечаем чаты с отказом как прочитанные
            try:
                filtered_chat_list = await filter_chats_uc.execute(
                    chat_list=chat_list,
                    headers=auth_data.headers,
                    cookies=auth_data.cookies,
                    user_id=user.id,
                    update_cookies_uc=update_cookies_uc,
                )
                
                logger.info(f"Чатов без отказа: {len(filtered_chat_list.items)}")
            except Exception as exc:
                logger.error(f"Ошибка при фильтрации чатов для пользователя {user.id}: {exc}", exc_info=True)
                continue
            
            # Берем первые чаты из отфильтрованного списка
            first_chats = filtered_chat_list.items
            if not first_chats:
                logger.info(f"Чаты не найдены для пользователя {user.id}")
                continue
            
            logger.info(f"Получаю детальную информацию о {len(first_chats)} чатах...")
            
            # Получаем детальную информацию о чатах
            chat_ids = [chat.id for chat in first_chats]
            try:
                chats_details: List[HHChatDetailed] = await fetch_chats_details_uc.execute(
                    chat_ids=chat_ids,
                    headers=auth_data.headers,
                    cookies=auth_data.cookies,
                    user_id=user.id,
                    update_cookies_uc=update_cookies_uc,
                )
                logger.info(f"Получено детальной информации о чатах: {len(chats_details)}")
            except Exception as exc:
                logger.error(f"Ошибка при получении детальной информации о чатах для пользователя {user.id}: {exc}", exc_info=True)
                continue
            
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
                
                logger.info(
                    f"Чаты сгруппированы: {len(chats_by_resume)} групп по резюме, "
                    f"{len(chats_without_resume)} чатов без резюме"
                )
                
                all_actions: List[AgentAction] = []
                
                # Обрабатываем каждую группу чатов с соответствующим резюме
                for resume_id, group_chats in chats_by_resume.items():
                    logger.info(
                        f"Обрабатываю группу из {len(group_chats)} чатов для резюме external_id={resume_id}"
                    )
                    
                    # Ищем резюме по external_id
                    resume = await uow.resume_repository.get_by_external_id(
                        external_id=resume_id,
                        user_id=user.id,
                    )
                    
                    if resume is None:
                        logger.warning(
                            f"Резюме с external_id={resume_id} не найдено, пропускаем группу чатов"
                        )
                        continue
                    
                    logger.info(
                        f"Используется резюме {resume.id} (external_id={resume_id}) "
                        f"для анализа {len(group_chats)} чатов"
                    )
                    
                    # Анализируем чаты этой группы с соответствующим резюме
                    try:
                        actions = await analyze_chats_uc.execute(
                            chats=group_chats,
                            resume=resume.content,
                            user_id=user.id,
                            user_parameters=resume.user_parameters,
                            resume_hash=resume.headhunter_hash,
                        )
                        
                        all_actions.extend(actions)
                        logger.info(
                            f"Сгенерировано {len(actions)} действий для группы резюме {resume_id}"
                        )
                    except Exception as exc:
                        logger.error(
                            f"Ошибка при анализе чатов для резюме {resume_id}: {exc}",
                            exc_info=True,
                        )
                        continue
                
                # Обрабатываем чаты без резюме (используем первое доступное резюме или пропускаем)
                if chats_without_resume:
                    logger.info(f"Обрабатываю {len(chats_without_resume)} чатов без резюме")
                    resumes = await uow.resume_repository.list_by_user_id(user.id)
                    if resumes:
                        resume = resumes[0]
                        logger.info(f"Используется первое резюме {resume.id} для чатов без резюме")
                        try:
                            actions = await analyze_chats_uc.execute(
                                chats=chats_without_resume,
                                resume=resume.content,
                                user_id=user.id,
                                user_parameters=resume.user_parameters,
                                resume_hash=resume.headhunter_hash,
                            )
                            all_actions.extend(actions)
                            logger.info(
                                f"Сгенерировано {len(actions)} действий для чатов без резюме"
                            )
                        except Exception as exc:
                            logger.error(
                                f"Ошибка при анализе чатов без резюме: {exc}",
                                exc_info=True,
                            )
                    else:
                        logger.warning("Нет резюме для обработки чатов без резюме, пропускаем")
                
                logger.info(f"Всего сгенерировано {len(all_actions)} действий для ответов")
                
                # Сохраняем действия в БД
                if all_actions:
                    # Создаём Event Publisher для уведомлений через WebSocket
                    from application.factories.event_factory import create_event_publisher
                    event_publisher = create_event_publisher()
                    
                    # Используем use case с уведомлениями
                    create_action_base_uc = CreateAgentActionUseCase(uow.standalone_agent_action_repository)
                    create_action_uc = CreateAgentActionWithNotificationUseCase(
                        create_agent_action_uc=create_action_base_uc,
                        event_publisher=event_publisher,
                    )
                    
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
                                message_to_str = (
                                    f" (ответ на сообщение {message_to})" if message_to else ""
                                )
                                logger.info(
                                    f"Сохранено действие: отправить сообщение в чат {dialog_id}{message_to_str}: {preview}"
                                )
                            elif action.type == "create_event":
                                event_type = action.data.get("event_type", "")
                                message = action.data.get("message", "")
                                preview = message[:100] + "..." if len(message) > 100 else message
                                logger.info(
                                    f"Сохранено действие: создать событие в чате {dialog_id}, "
                                    f"тип: {event_type}: {preview}"
                                )
                        except Exception as exc:
                            logger.error(
                                f"Ошибка при сохранении действия {action.id}: {exc}",
                                exc_info=True,
                            )
                            # Продолжаем сохранять остальные действия
                    
                    logger.info(f"Сохранено {saved_count} из {len(all_actions)} действий в БД")
                    
                    # Получаем настройки автоматизации для пользователя
                    get_automation_settings_uc = GetUserAutomationSettingsUseCase(
                        settings_repository=uow.user_automation_settings_repository
                    )
                    automation_settings = await get_automation_settings_uc.execute(user.id)
                    
                    # Если включена автоматическая отправка ответов на вопросы
                    if automation_settings.auto_reply_to_questions_in_chats:
                        logger.info(f"Автоматическая отправка ответов включена для пользователя {user.id}")
                        
                        # Создаем use cases для автоматической отправки
                        send_chat_message_uc = SendChatMessageUseCase(hh_client)
                        execute_agent_action_uc = ExecuteAgentActionUseCase(
                            agent_action_repository=uow.standalone_agent_action_repository,
                            send_chat_message_uc=send_chat_message_uc,
                        )
                        mark_as_sent_uc = MarkAgentActionAsSentUseCase(
                            agent_action_repository=uow.standalone_agent_action_repository
                        )
                        
                        # Автоматически отправляем сообщения для send_message действий
                        for action in all_actions:
                            if (
                                action.type == "send_message"
                                and action.data.get("sended") != True
                            ):
                                try:
                                    logger.info(
                                        f"Автоматическая отправка сообщения для действия {action.id}"
                                    )
                                    await execute_agent_action_uc.execute(
                                        action=action,
                                        headers=auth_data.headers,
                                        cookies=auth_data.cookies,
                                        user_id=user.id,
                                        update_cookies_uc=update_cookies_uc,
                                    )
                                    # Помечаем как отправленное
                                    await mark_as_sent_uc.execute(action)
                                    logger.info(
                                        f"Сообщение успешно отправлено для действия {action.id}"
                                    )
                                except Exception as exc:
                                    logger.error(
                                        f"Ошибка при автоматической отправке сообщения для действия {action.id}: {exc}",
                                        exc_info=True,
                                    )
                                    # Продолжаем работу, не прерываем цикл
                    else:
                        logger.info(f"Автоматическая отправка ответов выключена для пользователя {user.id}")
                else:
                    logger.info("Нет действий для сохранения")
                
                # Помечаем все чаты, которые были отправлены в агента, как прочитанные
                logger.info(f"Помечаю {len(chats_details)} чатов как прочитанные...")
                mark_read_tasks = []
                for chat in chats_details:
                    # Берем последнее сообщение из чата
                    if chat.messages and chat.messages.items:
                        last_message = chat.messages.items[-1]
                        if last_message and last_message.id:
                            async def mark_read_wrapper(chat_id: int, message_id: int) -> None:
                                try:
                                    await mark_chat_message_read_uc.execute(
                                        chat_id=chat_id,
                                        message_id=message_id,
                                        headers=auth_data.headers,
                                        cookies=auth_data.cookies,
                                        user_id=user.id,
                                        update_cookies_uc=update_cookies_uc,
                                    )
                                    logger.debug(
                                        f"Успешно помечено как прочитанное: "
                                        f"chat_id={chat_id}, message_id={message_id}"
                                    )
                                except Exception as exc:
                                    logger.warning(
                                        f"Ошибка при пометке чата {chat_id}, "
                                        f"сообщения {message_id} как прочитанного: {exc}"
                                    )
                            
                            task = asyncio.create_task(mark_read_wrapper(chat.id, last_message.id))
                            mark_read_tasks.append(task)
                        else:
                            logger.debug(
                                f"Не удалось пометить чат {chat.id} как прочитанный: "
                                f"отсутствует last_message или message_id"
                            )
                    else:
                        logger.debug(
                            f"Чат {chat.id} не имеет сообщений для пометки как прочитанного"
                        )
                
                if mark_read_tasks:
                    results = await asyncio.gather(*mark_read_tasks, return_exceptions=True)
                    success_count = len([r for r in results if not isinstance(r, Exception)])
                    logger.info(
                        f"Помечено {success_count} из {len(mark_read_tasks)} чатов как прочитанные"
                    )
            except Exception as exc:
                logger.error(f"Ошибка при анализе чатов для пользователя {user.id}: {exc}", exc_info=True)
                # Продолжаем обработку следующего пользователя
                continue


async def run_worker(config: AppConfig, shutdown_event: asyncio.Event | None = None) -> None:
    """Запустить воркер для анализа чатов.
    
    Args:
        config: Конфигурация приложения.
        shutdown_event: Событие для управления остановкой воркера. Если None, используется глобальное.
    """
    if shutdown_event is None:
        shutdown_event = globals()["shutdown_event"]
    
    logger.info("Запуск воркера анализа чатов")
    
    # Интервал между циклами (в секундах)
    cycle_delay_seconds = 60  # 1 минута между циклами
    
    try:
        while not shutdown_event.is_set():
            try:
                logger.info("Начало цикла обработки чатов")
                await process_chats_cycle(config)
                logger.info("Цикл обработки чатов завершен")
            except Exception as exc:
                logger.error(
                    f"Ошибка в цикле обработки чатов: {exc}",
                    exc_info=True,
                )
                # Продолжаем работу даже при ошибке
            
            # Ожидание до следующего цикла или сигнала завершения
            try:
                await asyncio.wait_for(
                    shutdown_event.wait(),
                    timeout=cycle_delay_seconds,
                )
                # Если событие установлено, выходим из цикла
                break
            except asyncio.TimeoutError:
                # Таймаут истек, продолжаем цикл
                continue
    
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания (Ctrl+C)")
    except Exception as exc:
        logger.error(f"Критическая ошибка воркера: {exc}", exc_info=True)
        raise
    finally:
        logger.info("Воркер завершает работу")


async def main() -> None:
    """Главная функция воркера (используется при запуске как отдельного процесса)."""
    # Получаем текущий event loop
    loop = asyncio.get_running_loop()
    
    # Регистрируем обработчики сигналов
    setup_signal_handlers(loop, shutdown_event)
    
    # Загружаем конфигурацию
    config = load_config()
    
    try:
        await run_worker(config, shutdown_event)
    except Exception as exc:
        logger.error(f"Критическая ошибка: {exc}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

