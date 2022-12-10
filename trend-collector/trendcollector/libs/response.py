from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from .client import CustomException


class HttpErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            resp: Response = await call_next(request)
        except CustomException as e:
            return JSONResponse(content=e.details, status_code=e.code)
        else:
            return resp
