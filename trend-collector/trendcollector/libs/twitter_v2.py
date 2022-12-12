import tweepy
from http import HTTPStatus
from .client import Twitter, TwitterAccount, CustomException

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
    api: tweepy.API
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
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)

    def get_me(self) -> TwitterAccount:
        try:
            resp = self.client.get_me()
            return TwitterAccount(resp[0]["id"], resp[0]["name"], resp[0]["username"])
        except tweepy.Unauthorized as e:
            raise TwitterUnAuthorized(e.response.status_code, FAILED_GET_MY_ACCOUNT, e.api_messages)
        except TimeoutError:
            raise IntervalServerError(HTTPStatus.INTERNAL_SERVER_ERROR, FAILED_GET_MY_ACCOUNT, [TIMEOUT_REQUEST])
        except Exception:
            raise IntervalServerError(HTTPStatus.INTERNAL_SERVER_ERROR, FAILED_GET_MY_ACCOUNT, [UNEXPECTED_ERROR])

    def get_account(self, account_id: int) -> TwitterAccount:
        try:
            resp = self.client.get_user(id=account_id)
            return TwitterAccount(resp[0]["id"], resp[0]["name"], resp[0]["username"])
        except tweepy.Unauthorized as e:
            raise TwitterUnAuthorized(e.response.status_code, FAILED_GET_MY_ACCOUNT, e.api_messages)
        except TimeoutError:
            raise IntervalServerError(HTTPStatus.INTERNAL_SERVER_ERROR, FAILED_GET_MY_ACCOUNT, [TIMEOUT_REQUEST])
        except Exception:
            raise IntervalServerError(HTTPStatus.INTERNAL_SERVER_ERROR, FAILED_GET_MY_ACCOUNT, [UNEXPECTED_ERROR])

    def list_trends(self) -> list[Trend]:
        try:
            resp = self.api.get_place_trends(23424856)[0]['trends']
        except Forbidden as e:
            self.logger.error(e)
            raise TwitterForbidden(HTTPStatus.INTERNAL_SERVER_ERROR, "トレンドリストの取得に失敗", [FORBIDDEN_ACCESS])
        else:
            return [Trend(name=t.name, url=t.url, query=t.query, tweet_volume=t.tweet_volume) for t in resp]
