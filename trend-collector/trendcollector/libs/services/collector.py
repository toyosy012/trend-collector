import abc

from .accessor import TwitterAccountAccessor, TrendAccessor
from ..client import Twitter
from ..models import Trend, TwitterAccount


class CollectorSvc(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_me(self) -> TwitterAccount: pass

    @abc.abstractmethod
    def update_me(self) -> TwitterAccount: pass

    @abc.abstractmethod
    def list_accounts(self) -> [TwitterAccount]: pass

    @abc.abstractmethod
    def get_account(self, account_id: int) -> TwitterAccount: pass

    @abc.abstractmethod
    def update_account(self, account: TwitterAccount) -> TwitterAccount: pass

    @abc.abstractmethod
    def get_trend(self, _id: int) -> Trend: pass

    @abc.abstractmethod
    def list_trends(self, page: int, counts: int) -> list[Trend]: pass

    @abc.abstractmethod
    def upsert_trends(self, woeid: int) -> [Trend]: pass

    @abc.abstractmethod
    def delete_trend(self, trend: Trend) -> bool: pass


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

    def list_accounts(self) -> [TwitterAccount]:
        return self.twitter_account_repo.list_accounts()

    def get_account(self, user_id: int) -> TwitterAccount:
        return self.twitter_account_repo.get_account(user_id)

    def update_account(self, user_id: int) -> TwitterAccount:
        old = self.twitter_account_repo.get_account(user_id)
        account = self.twitter_cli.get_account(user_id, old.account_id)
        return self.twitter_account_repo.update_account(account)

    def get_trend(self, _id: int) -> Trend:
        return self.trend_repo.get(_id)

    def list_trends(self, page: int, counts: int) -> list[Trend]:
        return self.trend_repo.list(page, counts)

    def upsert_trends(self, woeid: int) -> bool:
        trends = self.list_trends(woeid)
        return self.trend_repo.upsert(trends)

    def delete_trend(self, _id: int) -> bool:
        trend = self.get_trend(_id)
        return self.trend_repo.delete(trend.id)
