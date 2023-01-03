from datetime import datetime
from http import HTTPStatus
from logging import Logger

import tweepy
from injector import inject, singleton
from tweepy.client import Response

from ...models import (InputRawTrend, TrendMetrics, TrendQuery, TrendVolume,
                       TwitterAccount)
from ...services import client
from ...services.custom_exception import (FETCH_ERROR, Timeout,
                                          TwitterBadRequest, TwitterForbidden,
                                          TwitterNotFoundAccount,
                                          TwitterUnAuthorized)
from ..dependency_injector import Authentications

FAILED_FETCH_ACCOUNT = "自身のアカウントの取得に失敗"
FAILED_FETCH_TRENDS = "トレンドリストの取得に失敗"
FAILED_FETCH_TREND_METRICS = "トレンドメトリクスの取得に失敗"
NOT_FOUND_ACCOUNT = "Twitterアカウントが存在します"


@singleton
class TwitterV2(client.Twitter):
    api: tweepy.API
    client: tweepy.Client
    logger: Logger

    @inject
    def __init__(self, auths: Authentications):
        self.client = tweepy.Client(
            bearer_token=auths.bearer_token,
            consumer_key=auths.consumer_key, consumer_secret=auths.consumer_secret,
            access_token=auths.access_token, access_token_secret=auths.access_token_secret
        )
        auth = tweepy.OAuthHandler(auths.consumer_key, auths.consumer_secret)
        auth.set_access_token(auths.access_token, auths.access_token_secret)
        self.api = tweepy.API(auth)

    def get_me(self) -> TwitterAccount:
        try:
            resp: Response = self.client.get_me()
            return TwitterAccount(0, resp.data["id"], resp.data["name"], resp.data["username"])
        except tweepy.Unauthorized as e:
            raise TwitterUnAuthorized(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_ACCOUNT}", e.api_messages
            ) from e
        except tweepy.errors.Forbidden as e:
            raise TwitterForbidden(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_ACCOUNT}", e.api_messages
            ) from e
        except TimeoutError as e:
            raise Timeout(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_ACCOUNT}", list(e.args)
            ) from e

    def get_account(self, _id: int, account_id: int) -> TwitterAccount:
        try:
            resp: Response = self.client.get_user(id=account_id)
            if resp.data is None:
                raise TwitterNotFoundAccount(
                    HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_ACCOUNT}",
                    [f"Not Found twitter account: {account_id}"]
                )
            return TwitterAccount(_id, resp.data["id"], resp.data["name"], resp.data["username"])
        except tweepy.errors.BadRequest as e:
            raise TwitterBadRequest(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_ACCOUNT}", e.api_messages
            ) from e
        except tweepy.Unauthorized as e:
            raise TwitterUnAuthorized(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_ACCOUNT}", e.api_messages
            ) from e
        except tweepy.errors.Forbidden as e:
            raise TwitterForbidden(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_ACCOUNT}", e.api_messages
            ) from e
        except TimeoutError as e:
            raise Timeout(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_ACCOUNT}", list(e.args)
            ) from e

    def list_trends(self, woeid: int) -> [InputRawTrend]:
        try:
            resp = self.api.get_place_trends(woeid)[0]['trends']
            return [InputRawTrend(name=t["name"], query=t["query"]) for t in resp]
        except tweepy.errors.BadRequest as e:
            raise TwitterBadRequest(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_TRENDS}", e.api_messages
            ) from e
        except tweepy.Unauthorized as e:
            raise TwitterUnAuthorized(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_TRENDS}", e.api_messages
            ) from e
        except tweepy.errors.Forbidden as e:
            raise TwitterForbidden(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_TRENDS}", e.api_messages
            ) from e
        except TimeoutError as e:
            raise Timeout(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_TRENDS}", list(e.args)
            ) from e

    def list_trend_metrics(
            self, query: TrendQuery, start_time: datetime, end_time: datetime, granularity: str) -> TrendMetrics:
        try:
            volumes = self.client.get_recent_tweets_count(
                query.name, start_time=start_time.isoformat(), end_time=end_time.isoformat(), granularity=granularity
            )
        except tweepy.errors.BadRequest as e:
            raise TwitterBadRequest(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_TREND_METRICS}", e.api_messages
            ) from e
        except tweepy.errors.Unauthorized as e:
            raise TwitterUnAuthorized(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_TREND_METRICS}", e.api_messages
            ) from e
        except tweepy.errors.Forbidden as e:
            raise TwitterBadRequest(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_TREND_METRICS}", e.api_messages
            ) from e
        except TimeoutError as e:
            raise Timeout(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{FETCH_ERROR}: {FAILED_FETCH_TRENDS}", list(e.args)
            ) from e
        else:
            if len(volumes) <= 0:
                return TrendMetrics(query.trend_id, query.name, 0, [])

            volumes = [TrendVolume(v['tweet_count'], v["start"], v["end"]) for v in volumes.data]
            return TrendMetrics(query.trend_id, query.name, len(volumes), volumes)
