import logging
import uuid

from fastapi import Request, Response
from pylogrus import JsonFormatter, PyLogrus
from starlette.middleware.base import (BaseHTTPMiddleware,
                                       RequestResponseEndpoint)

from ..services import CustomException, APIErrorResponse


def config_logger(output: str) -> PyLogrus:
    enabled_fields = [
        'asctime',
        'function',
        'message',
        'stack_trace'
    ]
    formatter = JsonFormatter(datefmt='Z', enabled_fields=enabled_fields, sort_keys=True)
    handler = logging.FileHandler(output, encoding='utf-8')
    handler.setFormatter(formatter)

    logging.setLoggerClass(PyLogrus)
    logger: PyLogrus = logging.getLogger(__name__)  # setLoggerClassによりPyLogrusで生成
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def create_logging_handler(logger: PyLogrus):
    class _HttpLoggingMiddleware(BaseHTTPMiddleware):
        async def dispatch(
                self, request: Request, call_next: RequestResponseEndpoint
        ) -> Response:
            request_uuid = str(uuid.uuid4())
            body = await request.body()
            try:
                result = await call_next(request)
            except CustomException as e:
                logger.withFields(
                    {
                        'level': logging.getLevelName(logging.ERROR), 'code': e.code, 'details': e.details,
                        'stack_trace': e.stack_trace, 'path': str(request.url.path), 'body': str(body.decode()),
                        'uuid': request_uuid, 'user_agent': request.headers.get("User-Agent"), 'method': request.method
                    }
                ).exception("error")
                raise APIErrorResponse(e.code, e.message, request_uuid)
            else:
                return result
    return _HttpLoggingMiddleware
