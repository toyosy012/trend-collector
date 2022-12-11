import abc
from typing import List
from .accessor import DBAccessor
from ..client import Twitter, TwitterAccount


class CollectorSvc(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_me(self) -> TwitterAccount: pass

    @abc.abstractmethod
    def update_me(self) -> TwitterAccount: pass

    @abc.abstractmethod
    def list_accounts(self) -> List[TwitterAccount]: pass

    @abc.abstractmethod
    def get_account(self, account_id: int) -> TwitterAccount: pass

    @abc.abstractmethod
    def update_account(self, account: TwitterAccount) -> TwitterAccount: pass


class TwitterCollector(CollectorSvc):

    def __init__(self, db_accessor: DBAccessor, twitter_cli: Twitter):
        self.db_accessor = db_accessor
        self.twitter_cli = twitter_cli

    def get_me(self) -> TwitterAccount:
        return self.twitter_cli.get_me()

    def update_me(self) -> TwitterAccount:
        my_account = self.get_me()
        return self.db_accessor.update_account(my_account)

    def list_accounts(self) -> List[TwitterAccount]:
        return self.db_accessor.list_accounts()

    def get_account(self, account_id: int) -> TwitterAccount:
        return self.db_accessor.get_account(account_id)

    def update_account(self, account_id: int) -> TwitterAccount:
        account = self.twitter_cli.get_account(account_id)
        return self.db_accessor.update_account(account)

