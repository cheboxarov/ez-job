from __future__ import annotations

from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(slots=True)
class HHConfig:
    base_url: str = "https://api.hh.ru"
    max_vacancies: int = 50
    default_pages_depth: int = 1
    login_trust_flags_public_key: str = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEArfxXPfnUIiXXnopK1tHq
rYX4mjfSrM+m24rRcsIbZc0f9ZgZsca9cVy1afJe3f91FeJLKstE/hdexMLogUTq
7x0c/gDMQ8uqgptDpnkk5KHtSie47tE1LDV2qgJ8HUnVA+1uB9FJFiF0t4ppn8P2
fEt8L05lBn5Oe5tUVuLc5J52iBZAlY9AiHiAaRePcxHp8zlMGRjFoE7veeZMmlT8
IKDLYRMGxZ7HIPuRVFh3k1q5yKLAJ9BePoK8P/q7vBh+W1eYFA+q15q0Lna6h7C9
ZUA29wM1BYUwqQfRZldWxwy74XZE+WE9F5WoeIYzxnfTZzO87aeyfVaXA80uRAp0
l3+2GHORSVF5jmyag8i3ZnvIFFoO5pr/g6sKdimB72CYxS1nqdGDiJ1OIovKUI5w
VDlFeEgr+Ut8my5FVSlxLo7ZllrtRI0/RvXV91AqjyaTul4ZV2LjdpKRnofp01GV
aOYPatVR3bu6mBaf5y1E7aCPGLxTZwuZvgY4DYARNlzWLob+YARAt20s8fxb85/3
k8SG4+nYl4At9dtBQM0GA3fr6Xs6SSPK0DtS0p77/ddhqTFHTEX4IX4RAY6aMpc6
uaVq2CRxPYSj2aBfv+xCkAU5BI/9cftJKyXiD89oT/lkbUFPJDp8bxGipZ7Bwn2q
X2LjGaXPbBkAr9b7b+VZlMMCAwEAAQ==
-----END PUBLIC KEY-----"""


@dataclass(slots=True)
class OpenAIConfig:
    base_url: str = "https://bothub.chat/api/v2/openai/v1"
    model: str = "grok-4.1-fast"
    minimal_confidence: float = 0.0
    api_key: str | None = None
    resume_edit_model: str | None = None


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
class TelegramConfig:
    bot_token: str | None = "1938283998:AAH3ESJMT5hIyuzBBM5_CeKxiyGEZTrBtH0"
    bot_username: str | None = "wlovembot"
    link_token_ttl_seconds: int = 600
    frontend_url: str = "http://localhost:5173"


@dataclass(slots=True)
class AppConfig:
    hh: HHConfig
    openai: OpenAIConfig
    database: DatabaseConfig
    telegram: TelegramConfig


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
    
    # Дефолтный публичный ключ для login_trust_flags
    default_login_trust_flags_public_key = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEArfxXPfnUIiXXnopK1tHq
rYX4mjfSrM+m24rRcsIbZc0f9ZgZsca9cVy1afJe3f91FeJLKstE/hdexMLogUTq
7x0c/gDMQ8uqgptDpnkk5KHtSie47tE1LDV2qgJ8HUnVA+1uB9FJFiF0t4ppn8P2
fEt8L05lBn5Oe5tUVuLc5J52iBZAlY9AiHiAaRePcxHp8zlMGRjFoE7veeZMmlT8
IKDLYRMGxZ7HIPuRVFh3k1q5yKLAJ9BePoK8P/q7vBh+W1eYFA+q15q0Lna6h7C9
ZUA29wM1BYUwqQfRZldWxwy74XZE+WE9F5WoeIYzxnfTZzO87aeyfVaXA80uRAp0
l3+2GHORSVF5jmyag8i3ZnvIFFoO5pr/g6sKdimB72CYxS1nqdGDiJ1OIovKUI5w
VDlFeEgr+Ut8my5FVSlxLo7ZllrtRI0/RvXV91AqjyaTul4ZV2LjdpKRnofp01GV
aOYPatVR3bu6mBaf5y1E7aCPGLxTZwuZvgY4DYARNlzWLob+YARAt20s8fxb85/3
k8SG4+nYl4At9dtBQM0GA3fr6Xs6SSPK0DtS0p77/ddhqTFHTEX4IX4RAY6aMpc6
uaVq2CRxPYSj2aBfv+xCkAU5BI/9cftJKyXiD89oT/lkbUFPJDp8bxGipZ7Bwn2q
X2LjGaXPbBkAr9b7b+VZlMMCAwEAAQ==
-----END PUBLIC KEY-----"""
    
    hh_login_trust_flags_public_key = os.getenv("HH_LOGIN_TRUST_FLAGS_PUBLIC_KEY", default_login_trust_flags_public_key)

    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://bothub.chat/api/v2/openai/v1")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-oss-120b:exacto")
    openai_min_conf = _get_env_float("OPENAI_MIN_CONFIDENCE", 0.0)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    resume_edit_model = os.getenv("RESUME_EDIT_MODEL", "gpt-oss-120b:exacto")
    # resume_edit_model = os.getenv("RESUME_EDIT_MODEL", "glm-4.7")  # Опциональная модель для чата редактирования резюме

    # Нормализуем confidence в диапазон [0.0, 1.0]
    if openai_min_conf < 0.0:
        openai_min_conf = 0.0
    elif openai_min_conf > 1.0:
        openai_min_conf = 1.0

    hh_cfg = HHConfig(
        base_url=hh_base_url,
        max_vacancies=hh_max_vacancies,
        default_pages_depth=hh_default_pages_depth,
        login_trust_flags_public_key=hh_login_trust_flags_public_key,
    )
    openai_cfg = OpenAIConfig(
        base_url=openai_base_url,
        model=openai_model,
        minimal_confidence=openai_min_conf,
        api_key=openai_api_key,
        resume_edit_model=resume_edit_model,
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

    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN") or "8586542877:AAExU-pQjY47W4AEwTjR7O4gFhX_HFJdsGk"
    telegram_bot_username = os.getenv("TELEGRAM_BOT_USERNAME") or "autoofferai_bot"
    telegram_link_token_ttl = _get_env_int("TELEGRAM_LINK_TOKEN_TTL_SECONDS", 600)
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

    telegram_cfg = TelegramConfig(
        bot_token=telegram_bot_token,
        bot_username=telegram_bot_username,
        link_token_ttl_seconds=telegram_link_token_ttl,
        frontend_url=frontend_url,
    )

    return AppConfig(hh=hh_cfg, openai=openai_cfg, database=db_cfg, telegram=telegram_cfg)
