from typing import List
from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from pydantic import BaseModel, Field
from .client import CustomException


class Account(BaseModel):
    account_id: int = Field(default=0, example=0)
    name: str = Field(default="hogehoge", example="hogehoge")
    user_name: str = Field(default="@hogehoge", example="@hogehoge")


class ErrorReply(BaseModel):
    message: str = Field(None, example="hogehoge")
    details: List[str] = Field(None, example=[""])


class AccountReply(BaseModel):
    result: Account = Field(None, title="Account", example=Account())


class HttpErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            resp: Response = await call_next(request)
        except CustomException as e:
            return JSONResponse(
                status_code=e.code, content=jsonable_encoder(ErrorReply(message=e.message, details=e.details))
            )
        else:
            return resp
