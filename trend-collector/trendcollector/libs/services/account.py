from injector import inject, singleton

from ..services.accessor import TwitterAccount, TwitterAccountAccessor
from ..services.client import Twitter


@singleton
class TwitterAccountService:
    @inject
    def __init__(self, repo: TwitterAccountAccessor, cli: Twitter):
        self.account_repo = repo
        self.cli = cli

    def get_me(self) -> TwitterAccount:
        return self.cli.get_me()

    def update_me(self) -> TwitterAccount:
        my_account = self.get_me()
        return self.account_repo.update_account(my_account)

    def get(self, _id: int) -> TwitterAccount:
        return self.account_repo.get_account(_id)

    def list(self) -> list[TwitterAccount]:
        return self.account_repo.list_accounts()

    def update(self, _id: int) -> TwitterAccount:
        old = self.account_repo.get_account(_id)
        account = self.cli.get_account(_id, old.account_id)
        return self.account_repo.update_account(account)
