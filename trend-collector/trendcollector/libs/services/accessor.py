import abc
from typing import List
from ..models.twitter import TwitterAccount


class DBAccessor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_me(self) -> TwitterAccount: pass

    @abc.abstractmethod
    def update_me(self, account: TwitterAccount) -> TwitterAccount: pass

    @abc.abstractmethod
    def list_accounts(self) -> List[TwitterAccount]: pass

    @abc.abstractmethod
    def update_account(self, account: TwitterAccount) -> TwitterAccount: pass

    @abc.abstractmethod
    def get_account(self, account_id: int) -> TwitterAccount: pass
