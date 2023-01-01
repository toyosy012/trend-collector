from fastapi import Path

from ....response import AccountReply, AccountsReply, Account
from .....services.account import TwitterAccountService


class TwitterAccountRoutes:
    def __init__(self, account_svc: TwitterAccountService):
        self.account_svc = account_svc

    async def list_accounts(self):
        resp = self.account_svc.list()
        res = [Account(id=r.id, account_id=str(r.account_id), name=r.name, display_name=r.display_name) for r in resp]
        return AccountsReply(result=res)

    async def get_my_account(self):
        resp = self.account_svc.get_me()
        return AccountReply(
            result=Account(id=resp.id, account_id=str(resp.account_id), name=resp.name, display_name=resp.display_name))

    async def update_my_account(self):
        resp = self.account_svc.update_me()
        return AccountReply(
            result=Account(id=resp.id, account_id=str(resp.account_id), name=resp.name, display_name=resp.display_name))

    async def get_account(self, _id: int = Path(gt=0)):
        resp = self.account_svc.get(_id)
        return AccountReply(
            result=Account(id=resp.id, account_id=str(resp.account_id), name=resp.name, display_name=resp.display_name))

    async def update_account(self, _id: int = Path(gt=0)):
        resp = self.account_svc.update(_id)
        return AccountReply(
            result=Account(id=resp.id, account_id=str(resp.account_id), name=resp.name, display_name=resp.display_name))
