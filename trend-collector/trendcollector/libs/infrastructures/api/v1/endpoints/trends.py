from typing import Union

from ....response import TwitterTrend, TwitterTrendsReply, DeleteTrends, UpsertTrends
from .....services.collector import CollectorSvc


class TrendRoutes:
    def __init__(self, collector: CollectorSvc):
        self.collector = collector

    async def get_trend(self, _id: int):
        resp = self.collector.get_trend(_id)
        return TwitterTrend(id=resp.id, name=resp.name, query=resp.query, tweet_volume=resp.tweet_volume)

    async def list_trend(self, page: Union[int, None] = 1, counts: Union[int, None] = 20):
        resp = self.collector.list_trends(page, counts)
        return TwitterTrendsReply(
            result=[TwitterTrend(id=t.id, name=t.name, query=t.query, tweet_volume=t.tweet_volume) for t in resp],
            length=len(resp)
        )

    async def collect_current_trends(self, woeid: int):
        resp = self.collector.upsert_trends(woeid)
        return UpsertTrends(success=resp)

    async def delete_trend(self, _id: int):
        resp = self.collector.delete_trend(_id)
        return DeleteTrends(success=resp)
