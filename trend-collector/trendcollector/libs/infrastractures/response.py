from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from pydantic import BaseModel, Field

from ..infrastractures.conf import DISPLAY_NAME, USER_NAME, TREND_NAME, TREND_QUERY
from ..services import CustomException


class Token(BaseModel):
    token: str = Field(None, example="token")


class Account(BaseModel):
    user_id: int = Field(default=None, example=0)
    account_id: int = Field(default=0, example=0)
    name: str = Field(default=DISPLAY_NAME, example=DISPLAY_NAME)
    user_name: str = Field(default=USER_NAME, example=USER_NAME)


class TwitterTrend(BaseModel):
    id: int = Field(None, example=0)
    name: str = Field(None, example=TREND_NAME)
    query: str = Field(None, example=TREND_QUERY)
    tweet_volume: int = Field(None, example=1000)


class UpsertTrends(BaseModel):
    success: bool = Field(None, example=True)


class DeleteTrends(BaseModel):
    success: bool = Field(None, example=True)


class ErrorReply(BaseModel):
    message: str = Field(None, example="エラーが発生しました")
    details: list[str] = Field(None, example=["エラー原因を列挙"])


class AccountReply(BaseModel):
    result: Account = Field(None, title="Account", example=Account())


class AccountsReply(BaseModel):
    result: list[Account] = Field(None, title="Account", example=[Account()])


class TwitterTrendsReply(BaseModel):
    result: list[TwitterTrend] = Field(
        None, title="Trends", example=[TwitterTrend(id=0, name=TREND_NAME, query=TREND_QUERY, tweet_volume=0)])
    length: int = Field(None, title="Length", example=1)


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
