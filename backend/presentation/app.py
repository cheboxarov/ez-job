from __future__ import annotations

import asyncio
import signal
from contextlib import asynccontextmanager
from loguru import logger

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

from config import load_config
from infrastructure.auth.fastapi_users_setup import auth_backend, fastapi_users
from infrastructure.auth.schemas import UserCreate, UserRead, UserUpdate
from presentation.routers.dictionaries_router import router as dictionaries_router
from presentation.routers.hh_auth_router import router as hh_auth_router
from presentation.routers.resumes_router import router as resumes_router
from presentation.routers.users_router import router as users_router
from presentation.routers.vacancies_router import router
from presentation.routers.admin_router import router as admin_router
from workers.auto_reply_worker import run_worker as run_auto_reply_worker
from workers.chat_analysis_worker import run_worker as run_chat_analysis_worker
from workers.telegram_bot_worker import run_worker as run_telegram_bot_worker

# Настраиваем кастомную схему безопасности для Swagger
# Используем HTTPBearer вместо OAuth2 для простого поля ввода токена
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager для запуска и остановки воркеров."""
    # Startup: запускаем воркеры
    logger.info("Запуск воркеров в lifecycle FastAPI...")
    config = load_config()
    
    # Создаем события для управления остановкой воркеров
    chat_analysis_shutdown = asyncio.Event()
    auto_reply_shutdown = asyncio.Event()
    telegram_bot_shutdown = asyncio.Event()
    
    worker_shutdown_events = [chat_analysis_shutdown, auto_reply_shutdown, telegram_bot_shutdown]
    
    # Запускаем воркеры как фоновые задачи
    chat_analysis_task = asyncio.create_task(
        run_chat_analysis_worker(config, chat_analysis_shutdown)
    )
    auto_reply_task = asyncio.create_task(
        run_auto_reply_worker(config, auto_reply_shutdown)
    ) 
    telegram_bot_task = asyncio.create_task(
        run_telegram_bot_worker(config, telegram_bot_shutdown)
    )
    
    worker_tasks = [chat_analysis_task, auto_reply_task, telegram_bot_task]
    
    logger.info("Воркеры запущены")
    
    yield
    
    # Shutdown: останавливаем воркеры немедленно
    logger.info("Остановка воркеров...")
    
    # Устанавливаем события для остановки воркеров
    for event in worker_shutdown_events:
        event.set()
    
    # Немедленно отменяем все задачи воркеров
    if worker_tasks:
        logger.info("Отменяем все задачи воркеров...")
        for task in worker_tasks:
            if not task.done():
                task.cancel()
        
        # Ждем завершения отмены (немедленно, без таймаута)
        try:
            await asyncio.gather(*worker_tasks, return_exceptions=True)
            logger.info("Все воркеры остановлены")
        except Exception as exc:
            logger.warning(f"Ошибка при остановке воркеров: {exc}")


app = FastAPI(
    title="AutoOffer API",
    description="API для получения релевантных вакансий с сопроводительными письмами",
    version="1.0.0",
    lifespan=lifespan,
)

# Переопределяем OpenAPI схему для использования HTTPBearer вместо OAuth2
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Заменяем OAuth2 на HTTPBearer в схемах безопасности
    if "components" in openapi_schema and "securitySchemes" in openapi_schema["components"]:
        security_schemes = openapi_schema["components"]["securitySchemes"]
        
        # Заменяем все OAuth2 схемы на HTTPBearer
        for scheme_name, scheme_config in list(security_schemes.items()):
            if scheme_config.get("type") == "oauth2":
                # Удаляем старую OAuth2 схему
                del security_schemes[scheme_name]
                # Добавляем HTTPBearer схему с тем же именем
                security_schemes[scheme_name] = {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "Введите JWT токен (без префикса 'Bearer '). Получите токен через POST /auth/login"
                }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# CORS middleware для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры FastAPI Users
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# Подключаем наши роутеры
app.include_router(router)
app.include_router(users_router)
app.include_router(resumes_router)
app.include_router(dictionaries_router)
app.include_router(hh_auth_router)
app.include_router(admin_router)

# Subscription router
from presentation.routers.subscription_router import router as subscription_router

app.include_router(subscription_router)

# Chats router
from presentation.routers.chats_router import router as chats_router

app.include_router(chats_router)

# Agent Actions router
from presentation.routers.agent_actions_router import router as agent_actions_router

app.include_router(agent_actions_router)

# WebSocket router
from presentation.routers.websocket_router import router as websocket_router

app.include_router(websocket_router)

# Resume Edit WebSocket router
from presentation.routers.resume_edit_websocket_router import router as resume_edit_websocket_router

app.include_router(resume_edit_websocket_router)

# Telegram router
from presentation.routers.telegram_router import router as telegram_router

app.include_router(telegram_router)

# Automation router
from presentation.routers.automation_router import router as automation_router

app.include_router(automation_router)


@app.get("/")
async def root():
    """Корневой endpoint для проверки работы API."""
    return {"message": "AutoOffer API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

