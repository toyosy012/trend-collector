from pydantic import BaseSettings, validator

validate_error_format: str = "Validate error: {}"


class Environment(BaseSettings):
    access_token: str
    access_token_secret: str
    bearer_token: str
    consumer_key: str
    consumer_secret: str

    @classmethod
    @validator('*', pre=True)
    def exist(cls, v: str):
        if ' ' not in v:
            return ValueError()
        return v.title()
