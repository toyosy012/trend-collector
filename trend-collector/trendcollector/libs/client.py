import abc

from .models import Trend, TwitterAccount


class Twitter(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_me(self) -> TwitterAccount: pass

    @abc.abstractmethod
    def get_account(self, user_id: int, account_id: int) -> TwitterAccount: pass

    @abc.abstractmethod
    def list_trends(self, woeid: int) -> list[Trend]: pass

