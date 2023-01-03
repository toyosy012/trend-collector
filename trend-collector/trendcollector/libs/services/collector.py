import abc
from datetime import datetime
from typing import Union

from injector import inject, singleton

from ..models import InputRawTrend, TrendMetrics, TrendQuery, TrendSummary
from ..services.client import Twitter
from .accessor import TrendAccessor


class MediaCollectorSvc(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_trend(self, _id: int) -> TrendSummary:
        pass

    @abc.abstractmethod
    def list_trends(self, page: int, counts: int) -> list[TrendSummary]:
        pass

    @abc.abstractmethod
    def list_trend_metrics(
            self,
            trend_id: int,
            start_time: datetime,
            end_time: datetime,
            granularity: Union[str | None]
    ) -> TrendMetrics:
        pass

    @abc.abstractmethod
    def insert_trends(self, woeid: int) -> bool:
        pass

    @abc.abstractmethod
    def delete_trend(self, trend: int) -> bool:
        pass


@singleton
class TwitterCollector(MediaCollectorSvc):

    @inject
    def __init__(self, trend_repo: TrendAccessor, twitter_cli: Twitter):
        self.trend_repo = trend_repo
        self.twitter_cli = twitter_cli

    def get_trend(self, _id: int) -> TrendSummary:
        return self.trend_repo.get(_id)

    def list_trends(self, page: int, counts: int) -> list[TrendSummary]:
        return self.trend_repo.list(page, counts)

    def list_trend_metrics(
            self,
            trend_id: int,
            start_time: datetime,
            end_time: datetime,
            granularity: str
    ) -> TrendMetrics:
        trend = self.trend_repo.get(trend_id)
        query = TrendQuery(trend_id, trend.name)

        return self.twitter_cli.list_trend_metrics(query, start_time, end_time, granularity)

    def insert_trends(self, woeid: int) -> bool:
        trends: list[InputRawTrend] = self.twitter_cli.list_trends(woeid)
        return self.trend_repo.insert_trends(trends)

    def delete_trend(self, _id: int) -> bool:
        return self.trend_repo.delete(_id)
