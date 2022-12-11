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


class Twitter(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_me(self) -> TwitterAccount: pass

