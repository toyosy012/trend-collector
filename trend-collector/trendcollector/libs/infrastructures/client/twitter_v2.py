from datetime import datetime
from http import HTTPStatus
from logging import Logger

from injector import inject, singleton
import tweepy
from tweepy.client import Response

from ...models import TwitterAccount, InputRawTrend, TrendMetrics, TrendVolume, TrendQuery
from ...services import client
from ...services.custom_exception import Timeout, TwitterBadRequest, TwitterUnAuthorized, TwitterForbidden, FETCH_ERROR

FAILED_FETCH_ACCOUNT = "自身のアカウントの取得に失敗"
FAILED_FETCH_TRENDS = "トレンドリストの取得に失敗"
FAILED_FETCH_TREND_METRICS = "トレンドメトリクスの取得に失敗"


@singleton
class TwitterV2(client.Twitter):
    api: tweepy.API
    client: tweepy.Client
    logger: Logger

    @inject
    def __init__(
            self,
            bearer_token: str,
            consumer_key: str, consumer_secret: str,
            access_token: str, access_token_secret: str):
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=consumer_key, consumer_secret=consumer_secret,
            access_token=access_token, access_token_secret=access_token_secret
        )
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)

    def get_me(self) -> TwitterAccount:
        try:
            resp = self.client.get_me()
            return TwitterAccount(0, resp[0]["id"], resp[0]["name"], resp[0]["username"])
        except tweepy.Unauthorized as e:
            raise TwitterUnAuthorized(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_ACCOUNT}", e.api_messages)
        except tweepy.errors.Forbidden as e:
            raise TwitterForbidden(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_ACCOUNT}", e.api_messages)
        except TimeoutError as e:
            raise Timeout(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_ACCOUNT}", list(e.args))

    def get_account(self, _id: int, account_id: int) -> TwitterAccount:
        try:
            resp: Response = self.client.get_user(id=account_id)
            return TwitterAccount(_id, resp.data["id"], resp.data["name"], resp.data["username"])
        except tweepy.Unauthorized as e:
            raise TwitterUnAuthorized(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_ACCOUNT}", e.api_messages)
        except tweepy.errors.Forbidden as e:
            raise TwitterForbidden(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_ACCOUNT}", e.api_messages)
        except TimeoutError as e:
            raise Timeout(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_ACCOUNT}", list(e.args))

    def list_trends(self, woeid: int) -> [InputRawTrend]:
        try:
            resp = self.api.get_place_trends(woeid)[0]['trends']
            return [InputRawTrend(name=t["name"], query=t["query"]) for t in resp]
        except tweepy.errors.BadRequest as e:
            raise TwitterBadRequest(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_TRENDS}", e.api_messages)
        except tweepy.Unauthorized as e:
            raise TwitterUnAuthorized(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_TRENDS}", e.api_messages)
        except tweepy.errors.Forbidden as e:
            raise TwitterForbidden(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_TRENDS}", e.api_messages)
        except TimeoutError as e:
            raise Timeout(HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_TRENDS}", list(e.args))

    def list_trend_metrics(
            self, query: TrendQuery, start_time: datetime, end_time: datetime, granularity: str) -> TrendMetrics:
        try:
            volumes = self.client.get_recent_tweets_count(
                query.name, start_time=start_time.isoformat(), end_time=end_time.isoformat(), granularity=granularity
            )
        except tweepy.errors.BadRequest as e:
            raise TwitterBadRequest(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_TREND_METRICS}", e.api_messages)
        except tweepy.errors.Unauthorized as e:
            raise TwitterUnAuthorized(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_TREND_METRICS}", e.api_messages)
        except tweepy.errors.Forbidden as e:
            raise TwitterBadRequest(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_TREND_METRICS}", e.api_messages)
        except TimeoutError as e:
            raise Timeout(HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_TRENDS}", list(e.args))
        else:
            if len(volumes) <= 0:
                return TrendMetrics(query.trend_id, query.name, 0, [])

            volumes = [TrendVolume(v['tweet_count'], v["start"], v["end"]) for v in volumes.data]
            return TrendMetrics(query.trend_id, query.name, len(volumes), volumes)

