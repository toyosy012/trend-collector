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


class Trend:
    id: int
    name: str
    query: str
    tweet_volume: int | None

    def __init__(self, _id: int, name: str, query: str, tweet_volume: int | None):
        self.id = _id
        self.name = name
        self.query = query
        self.tweet_volume = tweet_volume if tweet_volume is not None else 0
