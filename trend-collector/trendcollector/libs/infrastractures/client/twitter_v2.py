import functools
from http import HTTPStatus
from logging import Logger

import tweepy
from tweepy.client import Response

from ...models import TwitterAccount, WoeidRawTrend
from ...services import CustomException, client

FORBIDDEN_ACCESS = "アクセス権限がないために失敗"
FAILED_GET_MY_ACCOUNT = "自身のアカウントの取得に失敗"
FAILED_GET_TRENDS = "トレンドリストの取得に失敗"
UNEXPECTED_ERROR = "予期せぬエラーが発生"
TIMEOUT_REQUEST = "リクエストタイムアウト"


class TwitterForbidden(CustomException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


class TwitterUnAuthorized(CustomException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


class IntervalServerError(CustomException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


def handle_exception(func):
    @functools.wraps(func)
    def _handler_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except tweepy.Unauthorized as e:
            raise TwitterUnAuthorized(HTTPStatus.INTERNAL_SERVER_ERROR, FAILED_GET_MY_ACCOUNT, e.api_messages)
        except tweepy.errors.Forbidden as e:
            raise TwitterForbidden(HTTPStatus.INTERNAL_SERVER_ERROR, FAILED_GET_TRENDS, e.api_messages)
        except TimeoutError as e:
            raise IntervalServerError(HTTPStatus.INTERNAL_SERVER_ERROR, FAILED_GET_MY_ACCOUNT, list(e.args))
        except Exception as e:
            raise IntervalServerError(HTTPStatus.INTERNAL_SERVER_ERROR, FAILED_GET_MY_ACCOUNT, list(e.args))

    return _handler_wrapper


class TwitterV2(client.Twitter):
    api: tweepy.API
    client: tweepy.Client
    logger: Logger

    def __init__(
            self,
            bearer_token: str,
            consumer_key: str, consumer_secret: str,
            access_token: str, access_token_secret: str,
            logger: Logger):
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=consumer_key, consumer_secret=consumer_secret,
            access_token=access_token, access_token_secret=access_token_secret,
        )
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)
        self.logger = logger

    @handle_exception
    def get_me(self) -> TwitterAccount:
        try:
            resp = self.client.get_me()
            return TwitterAccount(0, resp[0]["id"], resp[0]["name"], resp[0]["username"])
        except Exception as e:
            raise e

    @handle_exception
    def get_account(self, _id: int, account_id: int) -> TwitterAccount:
        try:
            resp: Response = self.client.get_user(id=account_id)
            return TwitterAccount(_id, resp.data["id"], resp.data["name"], resp.data["username"])
        except Exception as e:
            raise e

    @handle_exception
    def list_trends(self, woeid: int) -> list[WoeidRawTrend]:
        try:
            resp = self.api.get_place_trends(woeid)[0]['trends']
            return [WoeidRawTrend(name=t["name"], query=t["query"], tweet_volume=t["tweet_volume"]) for t in resp]
        except Exception as e:
            raise e
