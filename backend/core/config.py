import os


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Aurora Restaurante")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.4.0")
    API_PREFIX: str = os.getenv("API_PREFIX", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./aurora_restaurante.db")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "aurora_restaurante_chave_local")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "720"))

    CORS_ORIGINS: list[str] = ["*"]

    WS_CHANNELS: list[str] = [
        "mesas",
        "cozinha",
        "bar",
        "notificacoes",
        "caixa",
        "gerencia"
    ]


settings = Settings()