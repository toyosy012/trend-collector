import abc

from ..models import Trend, TwitterAccount, WoeidRawTrend
from ..services.client import Twitter
from .accessor import TrendAccessor, TwitterAccountAccessor


class CollectorSvc(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_me(self) -> TwitterAccount: pass

    @abc.abstractmethod
    def update_me(self) -> TwitterAccount: pass

    @abc.abstractmethod
    def list_accounts(self) -> list[TwitterAccount]: pass

    @abc.abstractmethod
    def get_account(self, account_id: int) -> TwitterAccount: pass

    @abc.abstractmethod
    def update_account(self, account_id: int) -> TwitterAccount: pass

    @abc.abstractmethod
    def get_trend(self, _id: int) -> Trend: pass

    @abc.abstractmethod
    def list_trends(self, page: int, counts: int) -> list[Trend]: pass

    @abc.abstractmethod
    def list_trend_metrics(
            self, trend_id: int, start_time: datetime, end_time: datetime, granularity: Union[str | None]
    ) -> TrendMetrics: pass

    @abc.abstractmethod
    def delete_trend(self, trend: int) -> bool: pass


class TwitterCollector(CollectorSvc):

    def __init__(self, trend_repo: TrendAccessor, twitter_accessor_repo: TwitterAccountAccessor, twitter_cli: Twitter):
        self.trend_repo = trend_repo
        self.twitter_account_repo = twitter_accessor_repo
        self.twitter_cli = twitter_cli

    def get_me(self) -> TwitterAccount:
        return self.twitter_cli.get_me()

    def update_me(self) -> TwitterAccount:
        my_account = self.get_me()
        return self.twitter_account_repo.update_account(my_account)

    def list_accounts(self) -> list[TwitterAccount]:
        return self.twitter_account_repo.list_accounts()

    def get_account(self, _id: int) -> TwitterAccount:
        return self.twitter_account_repo.get_account(_id)

    def update_account(self, _id: int) -> TwitterAccount:
        old = self.twitter_account_repo.get_account(_id)
        account = self.twitter_cli.get_account(_id, old.account_id)
        return self.twitter_account_repo.update_account(account)

    def get_trend(self, _id: int) -> Trend:
        return self.trend_repo.get(_id)

    def list_trends(self, page: int, counts: int) -> list[Trend]:
        return self.trend_repo.list(page, counts)

    def list_trend_metrics(self, trend_id: int,
                           start_time: datetime, end_time: datetime, granularity: str) -> TrendMetrics:
        trend = self.trend_repo.get(trend_id)
        query = TrendQuery(trend_id, trend.name)

        return self.twitter_cli.list_trend_metrics(query, start_time, end_time, granularity)

    def delete_trend(self, _id: int) -> bool:
        return self.trend_repo.delete(_id)
