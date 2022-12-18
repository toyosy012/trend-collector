from pydantic import BaseSettings, validator

TWITTER_ACCOUNT_ID = 1000000000000000
DISPLAY_NAME = "toyosy012"
USER_NAME = "toyosy012"
TREND_NAME = "ばあちゃん卒業"
TREND_QUERY = "%E3%81%B0%E3%81%82%E3%81%A1%E3%82%83%E3%82%93%E5%8D%92%E6%A5%AD"

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
