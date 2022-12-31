from fastapi import Path

from ....response import AccountReply, AccountsReply, Account
from .....services.collector import MediaCollectorSvc


class TwitterAccountRoutes:
    def __init__(self, collector: MediaCollectorSvc):
        self.media_collector = collector

    async def list_accounts(self):
        resp = self.media_collector.list_accounts()
        res = [Account(id=r.id, account_id=r.account_id, name=r.name, display_name=r.display_name) for r in resp]
        return AccountsReply(result=res)

    async def get_my_account(self):
        resp = self.media_collector.get_me()
        return AccountReply(
            result=Account(id=resp.id, account_id=resp.account_id, name=resp.name, display_name=resp.display_name))

    async def update_my_account(self):
        resp = self.media_collector.update_me()
        return AccountReply(
            result=Account(id=resp.id, account_id=resp.account_id, name=resp.name, display_name=resp.display_name))

    async def get_account(self, _id: int = Path(gt=0)):
        resp = self.media_collector.get_account(_id)
        return AccountReply(
            result=Account(id=resp.id, account_id=resp.account_id, name=resp.name, display_name=resp.display_name))

    async def update_account(self, _id: int = Path(gt=0)):
        resp = self.media_collector.update_account(_id)
        return AccountReply(
            result=Account(id=resp.id, account_id=resp.account_id, name=resp.name, display_name=resp.display_name))
