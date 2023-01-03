import abc
from typing import List

from ..models.twitter import InputRawTrend, TrendSummary, TwitterAccount

TWITTER_ACCOUNTS = "twitter_accounts"
FAILED_FETCH_ACCOUNT = "アカウントの取得に失敗"
FAILED_UPDATE_ACCOUNT = "アカウントの更新に失敗"
FAILED_FETCH_ACCOUNTS = "アカウントリストの取得に失敗"
FAILED_FETCH_TRENDS = "トレンドリストの取得に失敗"


class TwitterAccountAccessor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def list_accounts(self) -> list[TwitterAccount]:
        pass

    @abc.abstractmethod
    def update_account(self, account: TwitterAccount) -> TwitterAccount:
        pass

    @abc.abstractmethod
    def get_account(self, _id: int) -> TwitterAccount:
        pass


class TrendAccessor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get(self, _id: int) -> TrendSummary:
        pass

    @abc.abstractmethod
    def list(self, page: int, counts: int) -> List[TrendSummary]:
        pass

    @abc.abstractmethod
    def insert_trends(self, trends: List[InputRawTrend]) -> bool:
        pass

    @abc.abstractmethod
    def delete(self, _id: int) -> bool:
        pass
