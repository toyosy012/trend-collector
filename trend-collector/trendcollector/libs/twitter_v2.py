import tweepy
from http import HTTPStatus
from .client import Twitter, CustomException

FAILED_GET_MY_ACCOUNT = "自身のアカウントの取得に失敗"
UNEXPECTED_ERROR = "予期せぬエラーが発生"
TIMEOUT_REQUEST = "リクエストタイムアウト"


class TwitterUnAuthorized(CustomException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


class IntervalServerError(CustomException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


class TwitterV2(Twitter):
    client: tweepy.Client

    def __init__(
            self,
            bearer_token: str,
            consumer_key: str, consumer_secret: str,
            access_token: str, access_token_secret: str):
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=consumer_key, consumer_secret=consumer_secret,
            access_token=access_token, access_token_secret=access_token_secret,
        )

    def get_me(self):
        try:
            return self.client.get_me()
        except tweepy.Unauthorized as e:
            raise TwitterUnAuthorized(e.response.status_code, FAILED_GET_MY_ACCOUNT, e.api_messages)
        except TimeoutError as e:
            raise IntervalServerError(HTTPStatus.INTERNAL_SERVER_ERROR, FAILED_GET_MY_ACCOUNT, list(TIMEOUT_REQUEST))
        except Exception as e:
            raise IntervalServerError(HTTPStatus.INTERNAL_SERVER_ERROR, FAILED_GET_MY_ACCOUNT, list(UNEXPECTED_ERROR))
