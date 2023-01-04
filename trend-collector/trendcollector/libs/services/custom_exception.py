DELETE_ERROR = "削除エラー"
FETCH_ERROR = "取得エラー"
SEARCH_ERROR = "検索エラー"
UPDATE_ERROR = "更新エラー"


class CustomException(Exception):
    def __init__(self, code: int, message: str, details: list[str]):
        self.code = code
        self.message = message
        self.details = details


class RequestParamValidation(CustomException):
    def __init__(self, message: str, details: list[str]):
        super().__init__(422, message, details)


class TwitterException(CustomException):
    """There is no need to override '__init__'."""


class TwitterNotFoundAccount(TwitterException):
    """There is no need to override '__init__'."""


class TwitterBadRequest(TwitterException):
    """There is no need to override '__init__'."""


class TwitterUnAuthorized(CustomException):
    """There is no need to override '__init__'."""


class TwitterForbidden(TwitterException):
    """There is no need to override '__init__'."""


class IntervalServerException(CustomException):
    """There is no need to override '__init__'."""


class Timeout(IntervalServerException):
    """There is no need to override '__init__'."""


class DataBaseException(CustomException):
    """There is no need to override '__init__'."""


class DisconnectionDB(DataBaseException):
    """There is no need to override '__init__'."""


class NoTrendRecord(DataBaseException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, f"{message}: トレンドデータは存在しません", details)


class NoTwitterAccountRecord(DataBaseException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, f"{message}: Twitterアカウントデータは存在しません", details)


class APIErrorResponse(Exception):
    def __init__(self, code: int, message: str, request_id: str):
        self.code = code
        self.message = message
        self.request_id = request_id
