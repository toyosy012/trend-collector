import abc

from .custom_exception import CustomException
from ..models.twitter import Trend, TwitterAccount, WoeidRawTrend


TWITTER_ACCOUNTS = "twitter_accounts"
FAILED_FETCH_ACCOUNT = "アカウントの取得に失敗"
FAILED_UPDATE_ACCOUNT = "アカウントの更新に失敗"
FAILED_FETCH_ACCOUNTS = "アカウントリストの取得に失敗"
FAILED_FETCH_TRENDS = "トレンドリストの取得に失敗"


class DetachedInstance(CustomException):
    def __init__(self, code: int, message: str, details: [str]):
        super().__init__(code, message, details)


class InvalidRequestException(CustomException):
    def __init__(self, code: int, message: str, details: [str]):
        super().__init__(code, message, details)


class OperationalException(CustomException):
    def __init__(self, code: int, message: str, details: [str]):
        super().__init__(code, message, details)


class RuntimeException(CustomException):
    def __init__(self, code: int, message: str, details: [str]):
        super().__init__(code, message, details)


class TwitterAccountAccessor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def list_accounts(self) -> [TwitterAccount]: pass

    @abc.abstractmethod
    def update_account(self, account: TwitterAccount) -> TwitterAccount: pass

    @abc.abstractmethod
    def get_account(self, user_id: int) -> TwitterAccount: pass


class TrendAccessor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def list(self, page: int, counts: int) -> [Trend]: pass

    @abc.abstractmethod
    def get(self, _id: int) -> Trend: pass

    @abc.abstractmethod
    def upsert(self, trends: List[WoeidRawTrend]) -> bool: pass

    @abc.abstractmethod
    def delete(self, _id: int) -> bool: pass
