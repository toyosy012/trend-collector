import logging
import uuid

from fastapi import Request, Response
from injector import inject, singleton
from pylogrus import JsonFormatter, PyLogrus
from starlette.types import Message
from starlette.middleware.base import BaseHTTPMiddleware,  RequestResponseEndpoint

from ..services import CustomException, APIErrorResponse


@singleton
class LogCustomizer:
    @inject
    def __init__(self, output_path: str):
        self.output_path = output_path

    def _config_logger(self) -> PyLogrus:
        enabled_fields = [
            "asctime",
            "exception",
            "function",
            "message",
            "stacktrace",
            "levelname"
        ]
        formatter = JsonFormatter(datefmt="Z", enabled_fields=enabled_fields, sort_keys=True)
        handler = logging.FileHandler(self.output_path, encoding="utf-8")
        handler.setFormatter(formatter)

        logging.setLoggerClass(PyLogrus)
        logger: PyLogrus = logging.getLogger(__name__)  # setLoggerClassによりPyLogrusで生成
        logger.handlers = [handler]
        logger.setLevel(level=logging.INFO)
        return logger

    def create_logging_handler(self):
        logger = self._config_logger()

        class _HttpLoggingMiddleware(BaseHTTPMiddleware):
            async def dispatch(
                    self, request: Request, call_next: RequestResponseEndpoint
            ) -> Response:
                request_uuid = str(uuid.uuid4())
                body = await request.body()
                logger.withFields(
                    {
                        "path": str(request.url.path), "body": str(body.decode()),
                        "uuid": request_uuid, "user_agent": request.headers.get("User-Agent"), "method": request.method
                    }
                ).info("request")
                try:
                    async def receive() -> Message:
                        return {"type": "http.request", "body": body}
                    request._receive = receive
                    result = await call_next(request)
                except CustomException as e:
                    logger.withFields(
                        {
                            "code": e.code, "details": e.details,
                            "path": str(request.url.path), "body": str(body.decode()),
                            "uuid": request_uuid, "user_agent": request.headers.get("User-Agent"),
                            "method": request.method
                        }
                    ).exception("error")
                    raise APIErrorResponse(e.code, e.message, request_uuid)
                else:
                    logger.withFields(
                        {
                            "path": str(request.url.path), "uuid": request_uuid, "code": result.status_code,
                            "user_agent": request.headers.get("User-Agent"), "method": request.method
                        }
                    ).info("response")
                    return result

        return _HttpLoggingMiddleware
