"""Воркер для автоматической обработки откликов на вакансии."""

from __future__ import annotations

import asyncio
import signal
import sys
from pathlib import Path
from typing import Dict
from uuid import UUID

from loguru import logger

# Добавляем корневую директорию проекта в путь
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from config import AppConfig, load_config
from domain.use_cases.create_vacancy_response import CreateVacancyResponseUseCase
from domain.use_cases.generate_test_answers import GenerateTestAnswersUseCase
from domain.use_cases.process_auto_replies import ProcessAutoRepliesUseCase
from domain.use_cases.respond_to_vacancy import RespondToVacancyUseCase
from domain.use_cases.respond_to_vacancy_and_save import RespondToVacancyAndSaveUseCase
from infrastructure.agents.cover_letter_generator_agent import CoverLetterGeneratorAgent
from infrastructure.agents.vacancy_test_agent import VacancyTestAgent
from infrastructure.clients.hh_client import RateLimitedHHHttpClient
from application.factories.database_factory import create_unit_of_work
from application.factories.event_factory import create_event_publisher
from application.factories.search_and_get_filtered_vacancy_list_factory import (
    create_search_and_get_filtered_vacancy_list_usecase,
)

# Настройка loguru
logger.add(
    "logs/auto_reply_worker_{time}.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    enqueue=True,  # Для асинхронной записи
)

# Флаг для корректного завершения
shutdown_event = asyncio.Event()
# Счетчик для отслеживания повторных нажатий Ctrl+C
_sigint_count = 0


def setup_signal_handlers(loop: asyncio.AbstractEventLoop, shutdown_event: asyncio.Event) -> None:
    """Настройка обработчиков сигналов для корректного завершения."""
    global _sigint_count
    
    def signal_handler(signum: int) -> None:
        """Обработчик сигналов для корректного завершения."""
        global _sigint_count
        if signum == signal.SIGINT:
            _sigint_count += 1
            if _sigint_count == 1:
                logger.info(f"Получен сигнал {signum}, завершаем работу...")
                shutdown_event.set()
            elif _sigint_count >= 2:
                logger.warning("Принудительное завершение работы (второе нажатие Ctrl+C)...")
                sys.exit(1)
        else:
            logger.info(f"Получен сигнал {signum}, завершаем работу...")
            shutdown_event.set()
    
    # Используем add_signal_handler для правильной работы с asyncio
    if sys.platform != "win32":
        try:
            loop.add_signal_handler(signal.SIGINT, lambda: signal_handler(signal.SIGINT))
            loop.add_signal_handler(signal.SIGTERM, lambda: signal_handler(signal.SIGTERM))
        except NotImplementedError:
            # Если add_signal_handler не поддерживается, используем обычный signal
            signal.signal(signal.SIGINT, lambda s, f: signal_handler(s))
            signal.signal(signal.SIGTERM, lambda s, f: signal_handler(s))
    else:
        # На Windows используем signal.signal
        signal.signal(signal.SIGINT, lambda s, f: signal_handler(s))
        signal.signal(signal.SIGTERM, lambda s, f: signal_handler(s))


async def run_worker(config: AppConfig, shutdown_event: asyncio.Event | None = None) -> None:
    """Запустить воркер для обработки автооткликов.

    Args:
        config: Конфигурация приложения.
        shutdown_event: Событие для управления остановкой воркера. Если None, используется глобальное.
    """
    if shutdown_event is None:
        shutdown_event = globals()["shutdown_event"]
    
    logger.info("Запуск воркера автооткликов")

    # Создаем зависимости, которые не требуют UnitOfWork
    hh_client = RateLimitedHHHttpClient(base_url=config.hh.base_url)
    respond_to_vacancy_uc = RespondToVacancyUseCase(hh_client)
    event_publisher = create_event_publisher(config)

    # Фабрика для создания use case с unit_of_work (будет создаваться внутри контекста)
    def create_search_and_get_filtered_vacancy_list_usecase_with_uow(uow):
        return create_search_and_get_filtered_vacancy_list_usecase(config, unit_of_work=uow)

    # Словарь для отслеживания активных задач по resume_id
    active_tasks: Dict[UUID, asyncio.Task] = {}

    async def process_resume_task(resume_id: UUID, resume_data) -> None:
        """Обработать одно резюме в отдельной задаче.
        
        Args:
            resume_id: ID резюме.
            resume_data: Данные резюме.
        """
        try:
            # Проверяем shutdown_event перед началом обработки
            if shutdown_event.is_set():
                logger.info(f"Получен сигнал завершения, пропускаем обработку резюме {resume_id}")
                return
            
            # Создаем UnitOfWork для обработки этого резюме
            unit_of_work = create_unit_of_work(config.database)

            async with unit_of_work:
                # Проверяем shutdown_event еще раз перед созданием use case
                if shutdown_event.is_set():
                    logger.info(f"Получен сигнал завершения, прерываем обработку резюме {resume_id}")
                    return
                
                # Создаем агентов с unit_of_work для логирования вызовов LLM
                cover_letter_generator = CoverLetterGeneratorAgent(config.openai, unit_of_work=unit_of_work)
                vacancy_test_agent = VacancyTestAgent(config.openai, unit_of_work=unit_of_work)
                generate_test_answers_uc = GenerateTestAnswersUseCase(vacancy_test_agent)
                
                # Создаем use case с unit_of_work для логирования вызовов LLM
                search_and_get_filtered_vacancy_list_uc = create_search_and_get_filtered_vacancy_list_usecase_with_uow(unit_of_work)
                
                # Создаем Use Case с репозиториями из текущего UnitOfWork
                process_auto_replies_uc = ProcessAutoRepliesUseCase(
                    resume_repository=unit_of_work.resume_repository,
                    user_hh_auth_data_repository=unit_of_work.user_hh_auth_data_repository,
                    resume_filter_settings_repository=unit_of_work.resume_filter_settings_repository,
                    search_and_get_filtered_vacancy_list_uc=search_and_get_filtered_vacancy_list_uc,
                    cover_letter_generator=cover_letter_generator,
                    create_unit_of_work_factory=lambda: create_unit_of_work(config.database),
                    respond_to_vacancy_uc=respond_to_vacancy_uc,
                    hh_client=hh_client,
                    generate_test_answers_uc=generate_test_answers_uc,
                    event_publisher=event_publisher,
                    standalone_cookies_uow_factory=lambda: create_unit_of_work(config.database),
                    max_vacancies_per_resume=200,
                    delay_between_replies_seconds=30,
                )
                
                # Обрабатываем только это резюме
                await process_auto_replies_uc.process_single_resume(resume_data)
        except asyncio.CancelledError:
            logger.info(f"Задача для резюме {resume_id} отменена")
            raise
        except Exception as exc:
            logger.error(
                f"Ошибка при обработке резюме {resume_id}: {exc}",
                exc_info=True,
            )
        finally:
            # Удаляем задачу из словаря активных задач
            active_tasks.pop(resume_id, None)
            logger.info(f"Задача для резюме {resume_id} завершена и удалена из активных")

    # Основной цикл работы
    cycle_delay_seconds = 10  # 10 секунд между циклами

    try:
        while not shutdown_event.is_set():
            try:
                # Получаем список резюме с автооткликом
                unit_of_work = create_unit_of_work(config.database)
                async with unit_of_work:
                    resumes = await unit_of_work.resume_repository.get_all_active_auto_reply_resumes()
                    logger.info(f"Найдено резюме с автооткликом: {len(resumes)}")

                    # Сначала очищаем завершенные задачи из словаря
                    completed_resume_ids = [
                        resume_id 
                        for resume_id, task in active_tasks.items() 
                        if task.done()
                    ]
                    for resume_id in completed_resume_ids:
                        active_tasks.pop(resume_id, None)
                        logger.debug(f"Удалена завершенная задача для резюме {resume_id}")

                    # Проверяем shutdown_event перед запуском новых задач
                    if shutdown_event.is_set():
                        logger.info("Получен сигнал завершения, не запускаем новые задачи")
                        break

                    # Запускаем задачи только для резюме, у которых еще нет активной задачи
                    new_tasks_count = 0
                    for resume in resumes:
                        if shutdown_event.is_set():
                            logger.info("Получен сигнал завершения, прерываем запуск задач")
                            break
                        if resume.id not in active_tasks:
                            # Создаем новую задачу для этого резюме
                            task = asyncio.create_task(process_resume_task(resume.id, resume))
                            active_tasks[resume.id] = task
                            new_tasks_count += 1
                            logger.info(f"Запущена задача для резюме {resume.id}")
                        else:
                            logger.debug(
                                f"Для резюме {resume.id} уже есть активная задача, пропускаем"
                            )

                    logger.info(
                        f"Запущено новых задач: {new_tasks_count}, "
                        f"активных задач: {len(active_tasks)}"
                    )

                logger.info(
                    f"Цикл проверки завершен. Ожидание {cycle_delay_seconds} секунд до следующего цикла..."
                )
            except Exception as exc:
                logger.error(
                    f"Ошибка в цикле обработки автооткликов: {exc}",
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
        logger.info("Воркер завершает работу. Отмена всех задач...")
        
        try:
            current_task = asyncio.current_task()
            all_tasks = asyncio.all_tasks()
            tasks_to_cancel = [t for t in all_tasks if t is not current_task]

            if tasks_to_cancel:
                logger.info(f"Отмена {len(tasks_to_cancel)} незавершенных задач...")
                for task in tasks_to_cancel:
                    task.cancel()
                
                # Ждем завершения отмененных задач с коротким таймаутом
                logger.info("Ожидание завершения отмененных задач...")
                try:
                    await asyncio.wait_for(
                        asyncio.gather(*tasks_to_cancel, return_exceptions=True),
                        timeout=5,  # 5 секунд максимум
                    )
                    logger.info("Все задачи завершены")
                except asyncio.TimeoutError:
                    logger.warning(
                        "Таймаут ожидания завершения задач. Некоторые задачи могут быть прерваны принудительно."
                    )
            else:
                logger.info("Нет активных задач для отмены")
        except Exception as exc:
            logger.error(f"Ошибка при завершении воркера: {exc}", exc_info=True)
            
        logger.info("Воркер завершил работу")


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
