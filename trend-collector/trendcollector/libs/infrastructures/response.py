from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.middleware.base import (BaseHTTPMiddleware,
                                       RequestResponseEndpoint)

from ..infrastructures.conf import *
from ..services import APIErrorResponse


class Token(BaseModel):
    token: str = Field(None, example="token")


class Account(BaseModel):
    id: int = Field(None, example=1)
    account_id: int = Field(None, example=1000000000000000)
    name: str = Field(None, example=DISPLAY_NAME)
    display_name: str = Field(None, example=USER_NAME)


class TwitterTrend(BaseModel):
    id: int = Field(None, example=0)
    name: str = Field(None, example=TREND_NAME)
    query: str = Field(None, example=TREND_QUERY)
    tweet_volume: int = Field(None, example=1000)


class UpsertTrends(BaseModel):
    success: bool = Field(None, example=True)


class DeleteTrend(BaseModel):
    success: bool = Field(None, example=True)


class ErrorReply(BaseModel):
    message: str = Field(None, example="エラーが発生しました")
    request_id: str = Field(None, example="12345678-1234-5678-1234-567812345678")


class AccountReply(BaseModel):
    result: Account = Field(
        None, title="Account",
        example=Account(id=1, account_id=TWITTER_ACCOUNT_ID, name=USER_NAME, display_name=DISPLAY_NAME)
    )


class AccountsReply(BaseModel):
    result: list[Account] = Field(
        None, title="Account",
        example=[Account(id=1, account_id=TWITTER_ACCOUNT_ID, name=USER_NAME, display_name=DISPLAY_NAME)]
    )


class TwitterTrendsReply(BaseModel):
    result: list[TwitterTrend] = Field(
        None, title="Trends", example=[TwitterTrend(id=0, name=TREND_NAME, query=TREND_QUERY, tweet_volume=0)])
    length: int = Field(None, title="Length", example=1)


class HttpErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            result = await call_next(request)
        except APIErrorResponse as e:
            return JSONResponse(
                status_code=e.code, content=jsonable_encoder(ErrorReply(message=e.message, request_id=e.request_id))
            )
        else:
            return result
