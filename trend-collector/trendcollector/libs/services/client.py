import abc

from datetime import datetime

from ..models import InputRawTrend, TwitterAccount, TrendQuery, TrendMetrics


class Twitter(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_me(self) -> TwitterAccount: pass

    @abc.abstractmethod
    def get_account(self, _id: int, account_id: int) -> TwitterAccount: pass

    @abc.abstractmethod
    def list_trends(self, woeid: int) -> [InputRawTrend]: pass

    @abc.abstractmethod
    def list_trend_metrics(
            self, query: TrendQuery, start_time: datetime, end_time: datetime, granularity: str
    ) -> TrendMetrics: pass
