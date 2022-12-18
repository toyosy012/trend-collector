import abc
import functools
from typing import List

from ..models.twitter import Trend, TwitterAccount, WoeidRawTrend
from .custom_exception import CustomException

TWITTER_ACCOUNTS = "twitter_accounts"
FAILED_FETCH_ACCOUNT = "アカウントの取得に失敗"
FAILED_UPDATE_ACCOUNT = "アカウントの更新に失敗"
FAILED_FETCH_ACCOUNTS = "アカウントリストの取得に失敗"
FAILED_FETCH_TRENDS = "トレンドリストの取得に失敗"


class DetachedInstance(CustomException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


class InvalidRequestException(CustomException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


class OperationalException(CustomException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


class AttributesException(CustomException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


class RuntimeException(CustomException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


def add_exception_message(message: str):
    def _wrap_additional_message(func):
        @functools.wraps(func)
        def _add_exception_message(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except CustomException as e:
                raise CustomException(e.code, message, e.details)
        return _add_exception_message
    return _wrap_additional_message


class TwitterAccountAccessor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def list_accounts(self) -> list[TwitterAccount]: pass

    @abc.abstractmethod
    def update_account(self, account: TwitterAccount) -> TwitterAccount: pass

    @abc.abstractmethod
    def get_account(self, user_id: int) -> TwitterAccount: pass


class TrendAccessor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def list(self, page: int, counts: int) -> list[Trend]: pass

    @abc.abstractmethod
    def get(self, _id: int) -> Trend: pass

    @abc.abstractmethod
    def upsert(self, trends: List[WoeidRawTrend]) -> bool: pass

    @abc.abstractmethod
    def delete(self, _id: int) -> bool: pass
