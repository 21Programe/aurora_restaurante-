import os
import secrets
import warnings

from dotenv import load_dotenv


load_dotenv()


def _csv_env(name: str, default: str) -> list[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    APP_NAME = os.getenv("APP_NAME", "Aurora Restaurante")
    APP_VERSION = os.getenv("APP_VERSION", "2.0.0")
    API_PREFIX = os.getenv("API_PREFIX", "")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development").strip().lower()

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./aurora_restaurante.db",
    )

    SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "720")
    )

    CORS_ORIGINS = _csv_env(
        "CORS_ORIGINS",
        "http://127.0.0.1:8000,http://localhost:8000",
    )
    WS_CHANNELS = _csv_env(
        "WS_CHANNELS",
        "mesas,cozinha,bar,caixa,notificacoes,gerente",
    )


settings = Settings()

if not settings.SECRET_KEY:
    if settings.ENVIRONMENT == "production":
        raise RuntimeError(
            "SECRET_KEY precisa ser configurada no ambiente de produção."
        )

    settings.SECRET_KEY = secrets.token_urlsafe(48)
    warnings.warn(
        "SECRET_KEY não configurada. Uma chave temporária foi criada para "
        "desenvolvimento; os tokens expiram quando a API reinicia.",
        RuntimeWarning,
        stacklevel=2,
    )
