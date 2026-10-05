import os


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Aurora Restaurante")
    APP_VERSION: str = os.getenv("APP_VERSION", "2.0.0")
    API_PREFIX: str = os.getenv("API_PREFIX", "")

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./aurora_restaurante.db",
    )

    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "720")
    )

    # Em desenvolvimento local, os painéis web e o Expo podem ser liberados
    # explicitamente. Nunca usar "*" como padrão para produção.
    CORS_ORIGINS: list[str] = _csv(
        os.getenv(
            "CORS_ORIGINS",
            "http://127.0.0.1:8000,http://localhost:8000",
        )
    )

    WS_CHANNELS: list[str] = [
        "mesas",
        "cozinha",
        "bar",
        "notificacoes",
        "caixa",
        "gerencia",
    ]

    def validate(self) -> None:
        if not self.SECRET_KEY:
            raise RuntimeError(
                "SECRET_KEY não configurada. Defina a variável de ambiente antes de iniciar."
            )


settings = Settings()
