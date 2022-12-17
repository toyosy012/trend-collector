class CustomException(Exception):
    def __init__(self, code: int, message: str, details: list[str]):
        self.code = code
        self.message = message
        self.details = details
