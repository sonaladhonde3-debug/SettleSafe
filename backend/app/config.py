import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

class Settings:
    APP_NAME: str = "Real-Time Margin Call & Settlement Fail Predictor"
    API_V1_PREFIX: str = "/api/v1"

    # Model artifact
    MODEL_PATH: str = os.getenv("MODEL_PATH", str(BASE_DIR / "models" / "random_forest.pkl"))
    MODEL_EXPECTED_AUC: float = 0.85

    # Risk thresholds
    HIGH_RISK_PROBABILITY_THRESHOLD: float = float(os.getenv("HIGH_RISK_THRESHOLD", 0.65))
    HARD_MARGIN_BREACH_RATIO: float = float(os.getenv("HARD_MARGIN_BREACH_RATIO", 1.0))
    MIN_SETTLEMENT_BUFFER_HOURS: float = float(os.getenv("MIN_SETTLEMENT_BUFFER_HOURS", 2.0))
    MAX_COUNTERPARTY_EXPOSURE: float = float(os.getenv("MAX_COUNTERPARTY_EXPOSURE", 50_000_000))

    # Threadpool sizing for blocking sklearn calls
    MODEL_THREADPOOL_WORKERS: int = int(os.getenv("MODEL_THREADPOOL_WORKERS", 8))

    # WebSocket
    WS_HEARTBEAT_SECONDS: int = int(os.getenv("WS_HEARTBEAT_SECONDS", 15))

    # Redis backplane (only used if REDIS_URL is set; enables multi-instance WS sync)
    REDIS_URL: str | None = os.getenv("REDIS_URL")

    # Database connection
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "postgres")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "127.0.0.1")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
