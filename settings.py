import os
from typing import List

from envparse import env
from pydantic import AnyHttpUrl
from pathlib import Path

os.environ["TOKENIZERS_PARALLELISM"] = "false"


class BaseConfig:
    BASE_DIR = Path(__file__).resolve().parent
    APP_NAME: str = env("APP_NAME", "Email Fraud Detection API")
    APP_DESCRIPTION: str = env("APP_DESCRIPTION", "Email Fraud Detection API")
    APP_BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["*"]
    APP_VERSION: str = env("APP_VERSION", "1.0.0")
    APP_AUTH_TOKEN: str = env("APP_AUTH_TOKEN", "token")
    SWAGGER_UI: bool = env("SWAGGER_UI", True)

    DEVICE: str = env("DEVICE", "cpu")

    CELERY_BROKER_URL: str = env(
        "CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//"
    )
    CELERY_RESULT_BACKEND: str = env("CELERY_RESULT_BACKEND", "mongodb")
    CELERY_BACKEND_COL: str = env("CELERY_BACKEND_COL", default="taskmeta")

    # Mongo DB
    MONGO_HOST: str = env("MONGO_HOST", "localhost")
    MONGO_PORT: int = env("MONGO_PORT", 27017)
    MONGO_USERNAME: str = env("MONGO_USERNAME", "user")
    MONGO_PASSWORD: str = env("MONGO_SERVER_PASSWORD", "user")
    MONGO_DATABASE: str = env("MONGO_SERVER_DATABASE", "email_fraud_detection")

    FIX_TOKEN: str = env("FIX_TOKEN", "token")


settings = BaseConfig()
