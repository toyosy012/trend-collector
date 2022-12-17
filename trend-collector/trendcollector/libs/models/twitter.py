class TwitterAccount:
    user_id: int
    account_id: int
    name: str
    user_name: str

    def __init__(self, user_id: int, account_id: int, name: str, user_name: str):
        self.user_id = user_id
        self.account_id = account_id
        self.name = name
        self.user_name = user_name


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
