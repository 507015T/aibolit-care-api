import logging
import os
import structlog

from logging.handlers import RotatingFileHandler
from aibolit.core.config import settings


def configure_logging():
    os.makedirs(settings.LOGS_DIR, exist_ok=True)
    render_method = (
        structlog.dev.ConsoleRenderer()
        if settings.DEBUG
        else structlog.processors.JSONRenderer(indent=4, ensure_ascii=False)
    )
    file_handler = RotatingFileHandler(
        settings.LOGS_DIR / "app.log",
        mode="a",
        encoding="utf-8",
        backupCount=5,
        maxBytes=10 * 1024 * 1024,  # 10 MB
    )

    log_handlers = [logging.StreamHandler(), file_handler]
    logging.basicConfig(format="%(message)s", level=logging.INFO, handlers=log_handlers)
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.CallsiteParameterAdder(
                parameters=[
                    structlog.processors.CallsiteParameter.MODULE,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                ]
            ),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            render_method,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    return structlog.get_logger(name)
