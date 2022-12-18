import abc

from ..models import Trend, TwitterAccount, WoeidRawTrend
from ..services.client import Twitter
from .accessor import TrendAccessor, TwitterAccountAccessor, add_exception_message


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
    def update_account(self, account: TwitterAccount) -> TwitterAccount: pass

    @abc.abstractmethod
    def get_trend(self, _id: int) -> Trend: pass

    @abc.abstractmethod
    def list_trends(self, page: int, counts: int) -> list[Trend]: pass

    @abc.abstractmethod
    def upsert_trends(self, woeid: int) -> list[Trend]: pass

    @abc.abstractmethod
    def delete_trend(self, trend: Trend) -> bool: pass


class TwitterCollector(CollectorSvc):

    def __init__(self, trend_repo: TrendAccessor, twitter_accessor_repo: TwitterAccountAccessor, twitter_cli: Twitter):
        self.trend_repo = trend_repo
        self.twitter_account_repo = twitter_accessor_repo
        self.twitter_cli = twitter_cli

    @add_exception_message("自身のTwitterアカウントの取得に失敗")
    def get_me(self) -> TwitterAccount:
        return self.twitter_cli.get_me()

    @add_exception_message("自身のTwitterアカウントの更新に失敗")
    def update_me(self) -> TwitterAccount:
        my_account = self.get_me()
        return self.twitter_account_repo.update_account(my_account)

    @add_exception_message("アカウントリストの取得に失敗")
    def list_accounts(self) -> list[TwitterAccount]:
        return self.twitter_account_repo.list_accounts()

    @add_exception_message("Twitterアカウントの取得に失敗")
    def get_account(self, _id: int) -> TwitterAccount:
        return self.twitter_account_repo.get_account(_id)

    @add_exception_message("Twitterアカウントの更新に失敗")
    def update_account(self, _id: int) -> TwitterAccount:
        old = self.twitter_account_repo.get_account(_id)
        account = self.twitter_cli.get_account(_id, old.account_id)
        return self.twitter_account_repo.update_account(account)

    @add_exception_message("トレンドデータの取得に失敗")
    def get_trend(self, _id: int) -> Trend:
        return self.trend_repo.get(_id)

    @add_exception_message("トレンドデータリストの取得に失敗")
    def list_trends(self, page: int, counts: int) -> list[Trend]:
        return self.trend_repo.list(page, counts)

    @add_exception_message("トレンドデータリストの取得・更新に失敗")
    def upsert_trends(self, woeid: int) -> bool:
        trends: list[WoeidRawTrend] = self.twitter_cli.list_trends(woeid)
        return self.trend_repo.upsert(trends)

    @add_exception_message("トレンドデータリストの削除に失敗")
    def delete_trend(self, _id: int) -> bool:
        trend = self.get_trend(_id)
        return self.trend_repo.delete(trend.id)
