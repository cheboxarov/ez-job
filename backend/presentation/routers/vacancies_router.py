from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from application.services.vacancies_service import VacanciesService
from application.services.vacancy_responses_service import VacancyResponsesService
from config import AppConfig
from domain.entities.resume_filter_settings import ResumeFilterSettings
from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from presentation.dependencies import (
    get_cookies,
    get_current_user,
    get_headers,
    get_unit_of_work,
    get_vacancies_service,
    get_vacancy_responses_service,
    get_config,
)
from presentation.dto.vacancies_list_request import VacanciesListRequest
from presentation.dto.vacancies_list_response import (
    VacancyListItemResponse,
    VacanciesListResponse,
)
from presentation.dto.vacancies_request import VacanciesRequest
from presentation.dto.vacancies_response import VacancyResponse, VacanciesResponse
from presentation.dto.vacancy_respond_request import VacancyRespondRequest
from presentation.dto.vacancy_responses_list_response import (
    VacancyResponseItem,
    VacancyResponsesListResponse,
)
from presentation.dto.statistics_response import (
    StatisticsResponse,
    StatisticsDataPoint,
)
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase
from domain.use_cases.get_responses_statistics import GetResponsesStatisticsUseCase

router = APIRouter(prefix="/api/vacancies", tags=["vacancies"])


@router.post("/relevant", response_model=VacanciesResponse)
async def get_relevant_vacancies(
    request: VacanciesRequest,
    current_user=Depends(get_current_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
    vacancies_service: VacanciesService = Depends(get_vacancies_service),
    headers: dict[str, str] = Depends(get_headers),
    cookies: dict[str, str] = Depends(get_cookies),
    config: AppConfig = Depends(get_config),
) -> VacanciesResponse:
    """Получает релевантные вакансии с сопроводительными письмами.

    Доступен только для авторизованных пользователей.
    Клиент должен передать resume_id для использования резюме.

    Args:
        request: Параметры запроса для поиска вакансий (включая resume_id).
        current_user: Текущий авторизованный пользователь.
        unit_of_work: UnitOfWork для работы с БД.
        vacancies_service: Сервис для получения вакансий.
        headers: HTTP заголовки для запросов к HH API.
        cookies: HTTP cookies для запросов к HH API.
        config: Конфигурация приложения.

    Returns:
        Список отфильтрованных вакансий, отсортированных по confidence.

    Raises:
        HTTPException: 400 при ошибках валидации (незаполненные поля профиля),
            403 если резюме не принадлежит пользователю,
            500 при внутренних ошибках.
    """
    try:
        # Загружаем резюме и проверяем принадлежность
        resume = await unit_of_work.standalone_resume_repository.get_by_id(request.resume_id)
        if resume is None:
            raise HTTPException(
                status_code=404, detail=f"Резюме с ID {request.resume_id} не найдено"
            )

        if resume.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Доступ запрещен: резюме не принадлежит вам"
            )

        # Достаём настройки фильтров резюме
        settings = await unit_of_work.resume_filter_settings_repository.get_by_resume_id(
            request.resume_id
        )
        if settings is None:
            # Если настроек ещё нет, используем минимальный дефолт
            settings = ResumeFilterSettings(
                resume_id=request.resume_id,
                text=None,
                hh_resume_id=None,
                area=None,
                salary=None,
            )

        # Если фронт не передал список страниц, используем дефолтную глубину из конфига.
        if request.page_indices is None:
            depth = max(config.hh.default_pages_depth, 1)
            page_indices = list(range(depth))
        else:
            page_indices = request.page_indices

        # Создаем use case для обновления cookies
        update_cookies_uc = UpdateUserHhAuthCookiesUseCase(
            unit_of_work.standalone_user_hh_auth_data_repository
        )

        vacancies = await vacancies_service.get_relevant_vacancies_from_resume(
            resume=resume,
            filter_settings=settings,
            page_indices=page_indices,
            min_confidence_for_cover_letter=request.min_confidence_for_cover_letter,
            order_by=request.order_by,
            headers=headers,
            cookies=cookies,
            user_id=current_user.id,
            update_cookies_uc=update_cookies_uc,
        )

        # Маппинг из сущностей в DTO
        vacancy_responses = [
            VacancyResponse.from_entity(vacancy) for vacancy in vacancies
        ]

        return VacanciesResponse(count=len(vacancy_responses), items=vacancy_responses)

    except HTTPException:
        raise
    except ValueError as exc:
        logger.error(f"Ошибка валидации: {exc}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Внутренняя ошибка при получении вакансий: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при получении вакансий"
        ) from exc


@router.post("/relevant-list", response_model=VacanciesListResponse)
async def get_relevant_vacancy_list(
    request: VacanciesListRequest,
    current_user=Depends(get_current_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
    vacancies_service: VacanciesService = Depends(get_vacancies_service),
    headers: dict[str, str] = Depends(get_headers),
    cookies: dict[str, str] = Depends(get_cookies),
    config: AppConfig = Depends(get_config),
) -> VacanciesListResponse:
    """Получает релевантные list-вакансии (без детальных запросов).

    Доступен только для авторизованных пользователей.
    Клиент должен передать resume_id для использования резюме.
    Этот endpoint не делает запросы к /vacancies/{id}, только к /vacancies.

    Args:
        request: Параметры запроса для поиска вакансий (включая resume_id).
        current_user: Текущий авторизованный пользователь.
        unit_of_work: UnitOfWork для работы с БД.
        vacancies_service: Сервис для получения вакансий.
        headers: HTTP заголовки для запросов к HH API.
        cookies: HTTP cookies для запросов к HH API.
        config: Конфигурация приложения.

    Returns:
        Список отфильтрованных list-вакансий, отсортированных по confidence.

    Raises:
        HTTPException: 400 при ошибках валидации (незаполненные поля профиля),
            403 если резюме не принадлежит пользователю,
            500 при внутренних ошибках.
    """
    try:
        # Загружаем резюме и проверяем принадлежность
        resume = await unit_of_work.standalone_resume_repository.get_by_id(request.resume_id)
        if resume is None:
            raise HTTPException(
                status_code=404, detail=f"Резюме с ID {request.resume_id} не найдено"
            )

        if resume.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Доступ запрещен: резюме не принадлежит вам"
            )

        # Достаём настройки фильтров резюме
        settings = await unit_of_work.resume_filter_settings_repository.get_by_resume_id(
            request.resume_id
        )
        if settings is None:
            # Если настроек ещё нет, используем минимальный дефолт
            settings = ResumeFilterSettings(
                resume_id=request.resume_id,
                text=None,
                hh_resume_id=None,
                area=None,
                salary=None,
            )

        # Если фронт не передал список страниц, используем дефолтную глубину из конфига.
        if request.page_indices is None:
            depth = max(config.hh.default_pages_depth, 1)
            page_indices = list(range(depth))
        else:
            page_indices = request.page_indices

        # Создаем use case для обновления cookies
        update_cookies_uc = UpdateUserHhAuthCookiesUseCase(
            unit_of_work.standalone_user_hh_auth_data_repository
        )

        # Если min_confidence не передан, используем из конфига
        # (но он уже применяется в FilterVacancyListUseCase, так что здесь просто для совместимости)
        vacancies = await vacancies_service.get_relevant_vacancy_list_from_resume(
            resume=resume,
            filter_settings=settings,
            page_indices=page_indices,
            order_by=request.order_by,
            headers=headers,
            cookies=cookies,
            user_id=current_user.id,
            update_cookies_uc=update_cookies_uc,
        )

        # Маппинг из сущностей в DTO
        vacancy_responses = [
            VacancyListItemResponse.from_entity(vacancy) for vacancy in vacancies
        ]

        return VacanciesListResponse(count=len(vacancy_responses), items=vacancy_responses)

    except HTTPException:
        raise
    except ValueError as exc:
        logger.error(f"Ошибка валидации: {exc}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Внутренняя ошибка при получении list-вакансий: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при получении list-вакансий"
        ) from exc


@router.post("/respond")
async def respond_to_vacancy(
    request: VacancyRespondRequest,
    current_user=Depends(get_current_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
    vacancies_service: VacanciesService = Depends(get_vacancies_service),
    headers: dict[str, str] = Depends(get_headers),
    cookies: dict[str, str] = Depends(get_cookies),
    config: AppConfig = Depends(get_config),
) -> dict[str, Any]:
    """Откликнуться на вакансию в HeadHunter.

    Доступен только для авторизованных пользователей.
    Требует наличие headhunter_hash в резюме.

    Args:
        request: Параметры запроса для отклика (vacancy_id, resume_id, letter).
        current_user: Текущий авторизованный пользователь.
        unit_of_work: UnitOfWork для работы с БД.
        vacancies_service: Сервис для работы с вакансиями.
        headers: HTTP заголовки для запросов к HH API.
        cookies: HTTP cookies для запросов к HH API.
        config: Конфигурация приложения.

    Returns:
        Ответ от API HH после отклика.

    Raises:
        HTTPException: 400 при ошибках валидации,
            403 если резюме не принадлежит пользователю или отсутствует headhunter_hash,
            404 если резюме не найдено,
            500 при внутренних ошибках.
    """
    try:
        # Загружаем резюме и проверяем принадлежность
        resume = await unit_of_work.standalone_resume_repository.get_by_id(request.resume_id)
        if resume is None:
            raise HTTPException(
                status_code=404, detail=f"Резюме с ID {request.resume_id} не найдено"
            )

        if resume.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Доступ запрещен: резюме не принадлежит вам"
            )

        if not resume.headhunter_hash:
            raise HTTPException(
                status_code=400,
                detail="У резюме не указан headhunter_hash. Импортируйте резюме из HeadHunter.",
            )

        # Получаем base_url из конфига (может быть не задан, используем дефолт)
        internal_api_base_url = getattr(config.hh, "internal_api_base_url", None) or "https://krasnoyarsk.hh.ru"

        # Создаем RespondToVacancyAndSaveUseCase для сохранения отклика в БД
        from domain.use_cases.respond_to_vacancy import RespondToVacancyUseCase
        from domain.use_cases.respond_to_vacancy_and_save import RespondToVacancyAndSaveUseCase
        from domain.use_cases.create_vacancy_response import CreateVacancyResponseUseCase
        from domain.use_cases.check_and_update_subscription import (
            CheckAndUpdateSubscriptionUseCase,
        )
        from domain.use_cases.increment_response_count import (
            IncrementResponseCountUseCase,
        )
        from domain.exceptions.subscription_limit_exceeded import (
            SubscriptionLimitExceededError,
        )
        from infrastructure.clients.hh_client import RateLimitedHHHttpClient
        
        hh_client = RateLimitedHHHttpClient(base_url=config.hh.base_url)
        respond_to_vacancy_uc = RespondToVacancyUseCase(hh_client)
        # Используем standalone репозиторий, так как сохранение происходит после HTTP запроса
        # и не требует атомарности с другими операциями
        create_vacancy_response_uc = CreateVacancyResponseUseCase(
            vacancy_response_repository=unit_of_work.standalone_vacancy_response_repository
        )
        
        # Создаем use cases для проверки подписки и инкремента счетчика
        check_subscription_uc = CheckAndUpdateSubscriptionUseCase(
            user_subscription_repository=unit_of_work.user_subscription_repository,
            subscription_plan_repository=unit_of_work.subscription_plan_repository,
        )
        increment_response_count_uc = IncrementResponseCountUseCase(
            check_subscription_uc=check_subscription_uc,
            user_subscription_repository=unit_of_work.user_subscription_repository,
        )
        
        respond_to_vacancy_and_save_uc = RespondToVacancyAndSaveUseCase(
            respond_to_vacancy_uc=respond_to_vacancy_uc,
            create_vacancy_response_uc=create_vacancy_response_uc,
            check_subscription_uc=check_subscription_uc,
            increment_response_count_uc=increment_response_count_uc,
        )

        # Получаем название вакансии (если нужно, можно получить из HH API)
        vacancy_name = f"Вакансия {request.vacancy_id}"
        vacancy_url = None

        result = await respond_to_vacancy_and_save_uc.execute(
            vacancy_id=request.vacancy_id,
            resume_id=resume.id,
            user_id=current_user.id,
            resume_hash=resume.headhunter_hash,
            headers=headers,
            cookies=cookies,
            letter=request.letter,
            vacancy_name=vacancy_name,
            vacancy_url=vacancy_url,
            internal_api_base_url=internal_api_base_url,
        )

        return result

    except HTTPException:
        raise
    except SubscriptionLimitExceededError as exc:
        logger.warning(
            f"Лимит откликов исчерпан для user_id={current_user.id}: "
            f"{exc.count}/{exc.limit}"
        )
        raise HTTPException(
            status_code=429,
            detail={
                "message": str(exc),
                "count": exc.count,
                "limit": exc.limit,
                "seconds_until_reset": exc.seconds_until_reset,
            },
        ) from exc
    except ValueError as exc:
        logger.error(f"Ошибка валидации: {exc}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Внутренняя ошибка при отклике на вакансию: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при отклике на вакансию"
        ) from exc


@router.get("/responses", response_model=VacancyResponsesListResponse)
async def get_vacancy_responses(
    resume_hash: str,
    offset: int = 0,
    limit: int = 50,
    current_user=Depends(get_current_user),
    vacancy_responses_service: VacancyResponsesService = Depends(
        get_vacancy_responses_service
    ),
) -> VacancyResponsesListResponse:
    """Получить отправленные отклики на вакансии по резюме.

    Доступен только для авторизованных пользователей.
    Проверяет принадлежность резюме пользователю.

    Args:
        resume_hash: Hash резюме в HeadHunter (headhunter_hash).
        offset: Смещение для пагинации (по умолчанию 0).
        limit: Количество записей на странице (по умолчанию 50, максимум 100).
        current_user: Текущий авторизованный пользователь.
        vacancy_responses_service: Сервис для получения откликов.

    Returns:
        Список откликов с метаинформацией пагинации.

    Raises:
        HTTPException: 400 при невалидных параметрах пагинации,
            403 если резюме не принадлежит пользователю,
            404 если резюме не найдено,
            500 при внутренних ошибках.
    """
    try:
        logger.info(
            f"Запрос откликов: resume_hash={resume_hash}, user_id={current_user.id}, "
            f"offset={offset}, limit={limit}"
        )
        # Валидация параметров пагинации
        if offset < 0:
            raise HTTPException(
                status_code=400, detail="offset должен быть >= 0"
            )
        if limit <= 0:
            raise HTTPException(
                status_code=400, detail="limit должен быть > 0"
            )
        if limit > 100:
            raise HTTPException(
                status_code=400, detail="limit не должен превышать 100"
            )

        # Получаем отклики через сервис
        result = await vacancy_responses_service.get_responses_by_resume_hash(
            user_id=current_user.id,
            resume_hash=resume_hash,
            offset=offset,
            limit=limit,
        )

        logger.info(
            f"Получено откликов: {len(result.items)}, всего: {result.total}, "
            f"offset: {result.offset}, limit: {result.limit}"
        )

        # Преобразуем в DTO
        items = [
            VacancyResponseItem.from_entity(response) for response in result.items
        ]

        return VacancyResponsesListResponse(
            items=items,
            total=result.total,
            offset=result.offset,
            limit=result.limit,
        )

    except HTTPException:
        raise
    except ValueError as exc:
        error_message = str(exc)
        if "не найдено" in error_message or "не принадлежит" in error_message:
            status_code = 404 if "не найдено" in error_message else 403
            logger.warning(
                f"Ошибка доступа к откликам: {error_message} "
                f"(user_id={current_user.id}, resume_hash={resume_hash})"
            )
            raise HTTPException(status_code=status_code, detail=error_message) from exc
        logger.error(f"Ошибка валидации: {exc}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(
            f"Внутренняя ошибка при получении откликов: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при получении откликов"
        ) from exc


@router.get("/statistics", response_model=StatisticsResponse)
async def get_responses_statistics(
    days: int = 7,
    current_user=Depends(get_current_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
) -> StatisticsResponse:
    """Получить статистику откликов за последние N дней.

    Доступен только для авторизованных пользователей.
    Возвращает количество откликов по дням за указанный период.

    Args:
        days: Количество дней для статистики (по умолчанию 7, максимум 30).
        current_user: Текущий авторизованный пользователь.
        unit_of_work: UnitOfWork для работы с БД.

    Returns:
        Статистика откликов по дням.

    Raises:
        HTTPException: 400 при невалидных параметрах,
            500 при внутренних ошибках.
    """
    try:
        # Валидация параметров
        if days <= 0:
            raise HTTPException(
                status_code=400, detail="days должен быть > 0"
            )
        if days > 30:
            raise HTTPException(
                status_code=400, detail="days не должен превышать 30"
            )

        # Создаем use case
        get_statistics_uc = GetResponsesStatisticsUseCase(
            vacancy_response_repository=unit_of_work.vacancy_response_repository
        )

        # Получаем статистику
        statistics = await get_statistics_uc.execute(
            user_id=current_user.id,
            days=days,
        )

        # Преобразуем в DTO
        data_points = [
            StatisticsDataPoint(response_date=stat_date, count=count)
            for stat_date, count in statistics
        ]

        return StatisticsResponse(data=data_points)

    except HTTPException:
        raise
    except ValueError as exc:
        logger.error(f"Ошибка валидации: {exc}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(
            f"Внутренняя ошибка при получении статистики: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка при получении статистики"
        ) from exc

