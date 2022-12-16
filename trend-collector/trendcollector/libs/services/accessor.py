import abc
from typing import List
from ..models.twitter import Trend, TwitterAccount


class TwitterAccountAccessor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def list_accounts(self) -> List[TwitterAccount]: pass

    @abc.abstractmethod
    def update_account(self, account: TwitterAccount) -> TwitterAccount: pass

    @abc.abstractmethod
    def get_account(self, user_id: int) -> TwitterAccount: pass


class TrendAccessor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def list(self) -> list[Trend]: pass

    @abc.abstractmethod
    def get(self, _id: int) -> Trend: pass

    @abc.abstractmethod
    def update(self, trend: Trend) -> Trend: pass

    @abc.abstractmethod
    def delete(self, _id: int) -> bool: pass
