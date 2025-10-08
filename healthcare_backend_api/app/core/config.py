import os
from typing import List


class _Settings:
    """Application settings loaded from environment variables.

    Note:
        Do not read the .env file directly in code. The orchestrator provides the variables.
        For local development, copy .env.example to .env and set variables accordingly.
    """

    def __init__(self) -> None:
        self.MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.DB_NAME: str = os.getenv("DB_NAME", "healthcare")
        self.JWT_SECRET: str = os.getenv("JWT_SECRET", "CHANGE_ME_SECRET")
        self.JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
        self.CORS_ORIGINS: List[str] = self._parse_list(os.getenv("CORS_ORIGINS", ""))

        # Optional: path to custom indexes.json for ensuring MongoDB indexes
        self.INDEXES_FILE: str | None = os.getenv("INDEXES_FILE")

    @staticmethod
    def _parse_list(value: str) -> List[str]:
        return [v.strip() for v in value.split(",") if v.strip()]


# Singleton settings instance
settings = _Settings()
