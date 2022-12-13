from pydantic import BaseSettings, validator


DISPLAY_NAME = "toyosy012"
USER_NAME = "toyosy012"
TREND_NAME = "トレンド"
TREND_SEARCH_URL = "https://twitter.com/"
TREND_QUERY = "%E3%"

validate_error_format: str = "Validate error: {}"


class Environment(BaseSettings):
    access_token: str
    access_token_secret: str
    bearer_token: str
    consumer_key: str
    consumer_secret: str
    db_user: str
    db_pass: str
    db_name: str
    host: str
    port: int

    @classmethod
    @validator('*', pre=True)
    def exist(cls, v: str):
        if ' ' not in v:
            return ValueError()
        return v.title()
