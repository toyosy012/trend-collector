DELETE_ERROR = "削除エラー"
FETCH_ERROR = "取得エラー"
SEARCH_ERROR = "検索エラー"
UPDATE_ERROR = "更新エラー"


class CustomException(Exception):
    def __init__(self, code: int, message: str, details: list[str]):
        self.code = code
        self.message = message
        self.details = details


class TwitterException(CustomException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


class TwitterNotFoundAccount(TwitterException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


class TwitterBadRequest(TwitterException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


class TwitterUnAuthorized(CustomException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


class TwitterForbidden(TwitterException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


class IntervalServerException(CustomException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


class Timeout(IntervalServerException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


class DataBaseException(CustomException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


class DisconnectionDB(DataBaseException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


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
