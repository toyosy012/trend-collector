import abc

from typing import List

from .custom_exception import CustomException
from ..models.twitter import Trend, TwitterAccount


TWITTER_ACCOUNTS = "twitter_accounts"
FAILED_FETCH_ACCOUNT = "アカウントの取得に失敗"
FAILED_UPDATE_ACCOUNT = "アカウントの更新に失敗"
FAILED_FETCH_ACCOUNTS = "アカウントリストの取得に失敗"


class DetachedInstance(CustomException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


class OperationalException(CustomException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


class RuntimeException(CustomException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)

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
