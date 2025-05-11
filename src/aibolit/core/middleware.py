import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from structlog.contextvars import clear_contextvars
from aibolit.core.logger import get_logger
import structlog

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        trace_id = request.headers.get("X-TRACE-ID", str(uuid.uuid4()))
        structlog.contextvars.bind_contextvars(trace_id=trace_id)

        client_ip = request.client.host if request.client else "unknown"

        logger.info(
            "request_received",
            method=request.method,
            url=str(request.url),
            headers={k: v for k, v in request.headers.items() if k.lower() not in {"authorization", "cookie"}},
            query_params=dict(request.query_params),
            client_ip=client_ip,
            timestamp=start_time,
        )

        try:
            response = await call_next(request)
        except Exception as e:
            logger.error("unhandled_exception", error=str(e))
            raise
        finally:
            clear_contextvars()

        process_time = time.time() - start_time

        logger.info(
            "response_sent",
            status_code=response.status_code,
            process_time=round(process_time, 4),
            response_length=response.headers.get("content-length", "unknown"),
            response_timestamp=time.time(),
        )

        return response
