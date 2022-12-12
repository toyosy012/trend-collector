import abc


class CustomException(Exception):
    def __init__(self, code: int, message: str, details: list[str]):
        self.code = code
        self.message = message
        self.details = details


class TwitterAccount:
    account_id: int
    name: str
    user_name: str

    def __init__(self, account_id: int, name: str, user_name: str):
        self.account_id = account_id
        self.name = name
        self.user_name = user_name


class Trend:
    name: str
    url: str
    query: str
    tweet_volume: int | None

    def __init__(self, name: str, url: str, query: str, tweet_volume: int | None):
        self.name = name
        self.url = url
        self.query = query
        self.tweet_volume = tweet_volume if tweet_volume is not None else 0


class Twitter(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_me(self) -> TwitterAccount: pass

    @abc.abstractmethod
    def get_account(self, account_id: int) -> TwitterAccount: pass

    @abc.abstractmethod
    def list_trends(self) -> list[Trend]: pass

