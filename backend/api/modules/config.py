from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

logger.info("Загрузка переменных среды...")
load_dotenv()

class Config:
    SSH_TUNNELING: bool
    SSH_HOST: str | None
    SSH_USER: str | None
    SSH_PASSWORD: str | None
    SSH_PORT: int | None
    PG_HOST: str
    PG_PORT: int
    PG_USER: str
    PG_PASSWORD: str
    PG_DATABASE: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str
    OPENROUTER_MODEL: str
    MINIO_BUCKET: str
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_SECURE: bool
    MAX_IMAGE_SIZE: int
    MAX_IMAGE_COUNT: int
    MAX_CONTEXT_TOKENS: int
    MAX_OUTPUT_TOKENS: int
    LOGGING_SERVER_HOST: str
    LOGGING_SERVER_PORT: int

    def __init__(self):
        if os.getenv("SSH_TUNNELING").lower() in ["true", "1"]:
            self.SSH_TUNNELING = True
        else:
            self.SSH_TUNNELING = False
        self.SSH_HOST = os.getenv("SSH_HOST")
        self.SSH_USER = os.getenv("SSH_USER")
        self.SSH_PASSWORD = os.getenv("SSH_PASSWORD")
        self.SSH_PORT = int(os.getenv("SSH_PORT")) if not (os.getenv("SSH_PORT") is None) and os.getenv("SSH_PORT").isalnum() else None
        if not(self.SSH_PORT is None) and self.SSH_TUNNELING:
            if not (0 <= self.SSH_PORT <= 65535):
                raise ValueError("Порт SSH туннелирования не входит в диапазон 0-65535")
        self.PG_HOST = os.getenv("PG_HOST")
        self.PG_PORT = int(os.getenv("PG_PORT")) if not (os.getenv("PG_PORT") is None) and os.getenv("PG_PORT").isalnum() else None
        if not (0 <= self.PG_PORT <= 65535):
            raise ValueError("Порт базы данных не входит в диапазон 0-65535")
        self.PG_USER = os.getenv("PG_USER")
        self.PG_PASSWORD = os.getenv("PG_PASSWORD")
        self.PG_DATABASE = os.getenv("PG_DATABASE")
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.ALGORITHM = os.getenv("ALGORITHM")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
        if self.ACCESS_TOKEN_EXPIRE_MINUTES < 0:
            raise ValueError("Длительность действия токена не может быть меньше нуля")
        self.OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
        self.OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")
        self.OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")
        self.MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
        self.MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
        self.MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
        if os.getenv("MINIO_SECURE").lower() in ["true", "1"]:
            self.MINIO_SECURE = True
        else:
            self.MINIO_SECURE = False
        self.MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE"))
        if self.MAX_IMAGE_SIZE <= 0:
            raise ValueError("Максимальный размер файла должен быть больше нуля")
        self.MAX_IMAGE_COUNT = int(os.getenv("MAX_IMAGE_COUNT"))
        if self.MAX_IMAGE_COUNT <= 0:
            raise ValueError("Максимальное количество изображений должно быть больше нуля")
        self.MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS"))
        if self.MAX_CONTEXT_TOKENS <= 0:
            raise ValueError("Максимальное количество токенов контекста должно быть больше нуля")
        self.MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS"))
        if self.MAX_OUTPUT_TOKENS <= 0:
            raise ValueError("Максимальное количество выходных токенов должно быть больше нуля")
        self.LOGGING_SERVER_HOST = os.getenv("LOGGING_SERVER_HOST")
        self.LOGGING_SERVER_PORT = int(os.getenv("LOGGING_SERVER_PORT")) if not (os.getenv("LOGGING_SERVER_PORT") is None) and os.getenv("LOGGING_SERVER_PORT").isalnum() else None

logger.info("Создание экземпляра конфигураций...")
config_values = Config()
logger.info("Экземпляр конфигураций создан!")
