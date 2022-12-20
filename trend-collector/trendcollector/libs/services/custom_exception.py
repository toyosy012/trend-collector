class CustomException(Exception):
    def __init__(self, code: int, message: str, details: list[str], stack_trace: str | None):
        self.code = code
        self.message = message
        self.details = details
        self.stack_trace = stack_trace


class IntervalServerException(CustomException):
    def __init__(self, code: int, message: str, details: list[str], stack_trace: str | None):
        super().__init__(code, message, details, stack_trace)
