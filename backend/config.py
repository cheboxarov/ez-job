from __future__ import annotations

from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(slots=True)
class HHConfig:
    base_url: str = "https://api.hh.ru"
    max_vacancies: int = 50
    default_pages_depth: int = 1


@dataclass(slots=True)
class OpenAIConfig:
    base_url: str = "https://bothub.chat/api/v2/openai/v1"
    model: str = "grok-4.1-fast"
    minimal_confidence: float = 0.0
    api_key: str | None = None


@dataclass(slots=True)
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    database: str = "hh_db"
    db_url: str | None = None

    def get_db_url(self) -> str:
        """Получить URL подключения к БД."""
        if self.db_url:
            return self.db_url
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass(slots=True)
class AppConfig:
    hh: HHConfig
    openai: OpenAIConfig
    database: DatabaseConfig


def _get_env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _get_env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def load_config() -> AppConfig:
    """Загрузка общего конфига приложения из переменных окружения с дефолтами."""

    # Подтягиваем переменные из .env (если файл есть)
    load_dotenv()

    # Важно: нельзя использовать классовые атрибуты dataclass со slots в качестве дефолтов
    # (они становятся дескрипторами). Поэтому дефолты задаём явно.
    hh_base_url = os.getenv("HH_BASE_URL", "https://api.hh.ru")
    hh_max_vacancies = _get_env_int("HH_MAX_VACANCIES", 50)
    hh_default_pages_depth = _get_env_int("HH_DEFAULT_PAGES_DEPTH", 1)

    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://bothub.chat/api/v2/openai/v1")
    openai_model = os.getenv("OPENAI_MODEL", "grok-4.1-fast")
    openai_min_conf = _get_env_float("OPENAI_MIN_CONFIDENCE", 0.0)
    openai_api_key = os.getenv("OPENAI_API_KEY")

    # Нормализуем confidence в диапазон [0.0, 1.0]
    if openai_min_conf < 0.0:
        openai_min_conf = 0.0
    elif openai_min_conf > 1.0:
        openai_min_conf = 1.0

    hh_cfg = HHConfig(
        base_url=hh_base_url,
        max_vacancies=hh_max_vacancies,
        default_pages_depth=hh_default_pages_depth,
    )
    openai_cfg = OpenAIConfig(
        base_url=openai_base_url,
        model=openai_model,
        minimal_confidence=openai_min_conf,
        api_key=openai_api_key,
    )

    # Конфигурация БД
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = _get_env_int("DB_PORT", 5432)
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_name = os.getenv("DB_NAME", "hh_db")
    db_url = os.getenv("DB_URL")  # Опциональный прямой URL

    db_cfg = DatabaseConfig(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_name,
        db_url=db_url,
    )

    return AppConfig(hh=hh_cfg, openai=openai_cfg, database=db_cfg)
