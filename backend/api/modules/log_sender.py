from fluent import handler
import logging

from .config import config_values

logger = logging.getLogger(__name__)

def setup_logging():
    """Запуск отправки логов на сервер логирования"""
    logger.info("Подключение к базе логирования...")
    try:
        fluent_handler = handler.FluentHandler("api.logs", host=config_values.LOGGING_SERVER_HOST, port=config_values.LOGGING_SERVER_PORT)
    except Exception as e:
        raise ValueError(f"Ошибка подключения к серверу логирования: {e}")
    logger.info("База логирования подключена!")

    formatter = handler.FluentRecordFormatter()
    fluent_handler.setFormatter(formatter)
    fluent_handler.setLevel(logging.INFO)

    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn").addHandler(fluent_handler)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").addHandler(fluent_handler)
