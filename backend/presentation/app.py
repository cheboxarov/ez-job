from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

from infrastructure.auth.fastapi_users_setup import auth_backend, fastapi_users
from infrastructure.auth.schemas import UserCreate, UserRead, UserUpdate
from presentation.routers.dictionaries_router import router as dictionaries_router
from presentation.routers.hh_auth_router import router as hh_auth_router
from presentation.routers.resumes_router import router as resumes_router
from presentation.routers.users_router import router as users_router
from presentation.routers.vacancies_router import router

# Настраиваем кастомную схему безопасности для Swagger
# Используем HTTPBearer вместо OAuth2 для простого поля ввода токена
security = HTTPBearer()

app = FastAPI(
    title="Вкатился API",
    description="API для получения релевантных вакансий с сопроводительными письмами",
    version="1.0.0",
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


@app.get("/")
async def root():
    """Корневой endpoint для проверки работы API."""
    return {"message": "Вкатился API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

