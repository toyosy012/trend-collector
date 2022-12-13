from typing import List
from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from pydantic import BaseModel, Field
from .client import CustomException
from .conf import *


class Token(BaseModel):
    token: str = Field(None, example="token")


class Account(BaseModel):
    account_id: int = Field(default=0, example=0)
    name: str = Field(default=DISPLAY_NAME, example=DISPLAY_NAME)
    user_name: str = Field(default=USER_NAME, example=USER_NAME)


class TwitterTrend(BaseModel):
    name: str = Field(default=TREND_NAME, example=TREND_NAME)
    url: str = Field(default=TREND_SEARCH_URL, example=TREND_SEARCH_URL)
    query: str = Field(default=TREND_QUERY, example=TREND_QUERY)
    tweet_volume: int = Field(default=0, example=1000)


class ErrorReply(BaseModel):
    message: str = Field(None, example="hogehoge")
    details: List[str] = Field(None, example=[""])


class AccountReply(BaseModel):
    result: Account = Field(None, title="Account", example=Account())


class AccountsReply(BaseModel):
    result: List[Account] = Field(None, title="Account", example=[Account()])


class TwitterTrendsReply(BaseModel):
    result: list[TwitterTrend] = Field(None, title="Trends", example=[TwitterTrend()])


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
