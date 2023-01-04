from datetime import datetime
from typing import Union

from fastapi import Path, Query
from pydantic import BaseModel

from .....infrastructures.response import (DeleteTrend, TrendCommandResult,
                                           TrendMetrics, TrendSummaries,
                                           TrendSummary, TrendVolume)
from .....services.collector import MediaCollectorSvc


class TwitterWoeid(BaseModel):
    woeid: int


class TrendRoutes:
    def __init__(self, collector: MediaCollectorSvc):
        self.media_collector = collector

    async def get_trend(self, _id: int = Path(gt=0)) -> TrendSummary:
        resp = self.media_collector.get_trend(_id)
        return TrendSummary(id=resp.id, name=resp.name, updated_at=resp.updated_at)

    async def list_trend(
            self,
            page: Union[int, None] = Query(1, gt=0),
            counts: Union[int, None] = Query(20, gt=0)
    ) -> TrendSummaries:
        resp = self.media_collector.list_trends(page, counts)
        trends = [TrendSummary(id=t.id, name=t.name, updated_at=t.updated_at) for t in resp] if 0 < len(resp) else []

        return TrendSummaries(result=trends, length=len(trends))

    async def list_trend_metrics(
            self,
            start_time_utc: datetime,
            end_time_utc: datetime,
            _id: int = Path(gt=0),
            granularity: Union[str, None] = Query("hour", regex="^(minute|hour|day)$")
    ) -> TrendMetrics:

        trend_detail = self.media_collector.list_trend_metrics(_id, start_time_utc, end_time_utc, granularity)
        volumes = [TrendVolume(volume=v.volume, start=v.start, end=v.end) for v in trend_detail.volumes]
        return TrendMetrics(
            id=trend_detail.id, name=trend_detail.name, total=trend_detail.total, volumes=volumes)

    async def insert_trend(self, body: TwitterWoeid) -> TrendCommandResult:
        result = self.media_collector.insert_trends(body.woeid)
        return TrendCommandResult(success=result)

    async def delete_trend(self, _id: int = Path(gt=0)):
        resp = self.media_collector.delete_trend(_id)
        return DeleteTrend(success=resp)
