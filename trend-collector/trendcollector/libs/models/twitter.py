from datetime import datetime
from typing import List


class TwitterAccount:
    id: int
    account_id: int
    name: str
    display_name: str

    def __init__(self, _id: int, account_id: int, name: str, display_name: str):
        self.id = _id
        self.account_id = account_id
        self.name = name
        self.display_name = display_name


class WoeidRawTrend:
    name: str
    query: str
    tweet_volume: int | None

    def __init__(self, name: str, query: str, tweet_volume: int | None):
        self.name = name
        self.query = query
        self.tweet_volume = tweet_volume if tweet_volume is not None else 0


class TrendSummary:
    id: int
    name: str
    updated_at: datetime

    def __init__(self, _id: int, name: str, updated_at: datetime):
        self.id = _id
        self.name = name
        self.updated_at = updated_at


class TrendVolume:
    volume: int
    start: datetime
    end: datetime

    def __init__(self, volume: int | None, start: datetime, end: datetime):
        self.start = start
        self.end = end
        self.volume = volume if volume is not None else 0


class TrendMetrics:
    id: int
    name: str
    total: int
    volumes: [TrendVolume]

    def __init__(self, _id: int, name: str, total: int, volumes: List[TrendVolume]):
        self.id = _id
        self.name = name
        self.total = total
        self.volumes = volumes


class TrendQuery:
    trend_id: int
    name: str

    def __init__(self, trend_id: int, name: str):
        self.trend_id = trend_id
        self.name = name
