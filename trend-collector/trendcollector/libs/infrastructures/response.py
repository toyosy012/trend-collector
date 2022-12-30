from datetime import datetime
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


class TrendSummary(BaseModel):
    id: int = Field(None, example=RECORD_ID)
    name: str = Field(None, example=TREND_NAME)
    updated_at: datetime = Field(None, example=datetime.strptime(INPUT_DATETIME, INPUT_DATETIME_FORMAT))


class TrendSummaries(BaseModel):
    result: list[TrendSummary] = Field(
        None,
        title="TrendSummaries",
        example=[
            TrendSummary(
                id=RECORD_ID, name=TREND_NAME, updated_at=datetime.strptime(INPUT_DATETIME, INPUT_DATETIME_FORMAT)
            )
        ]
    )
    length: int = Field(None, title="Length", example=1)


class UpsertTrends(BaseModel):
    success: bool = Field(None, example=True)


class DeleteTrend(BaseModel):
    success: bool = Field(None, example=True)


class TrendVolume(BaseModel):
    volume: int = Field(None, example=TREND_VOLUME)
    start: datetime = Field(None, example=datetime.strptime(START_DATETIME, INPUT_DATETIME_FORMAT))
    end: datetime = Field(None, example=datetime.strptime(END_DATETIME, INPUT_DATETIME_FORMAT))


class TrendMetrics(BaseModel):
    id: int = Field(None, example=RECORD_ID)
    name: str = Field(None, example=TREND_NAME)
    total: int = Field(None, example=1)
    volumes: list[TrendVolume] = Field(
        None, example=[
            TrendVolume(
                volume=TREND_VOLUME,
                start=datetime.strptime(START_DATETIME, INPUT_DATETIME_FORMAT),
                end=datetime.strptime(END_DATETIME, INPUT_DATETIME_FORMAT)
            )
        ]
    )


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
