from sqlalchemy import Column, DATETIME, Integer, String
from sqlalchemy.ext.declarative import declarative_base


TWITTER_ACCOUNTS = "twitter_accounts"


base = declarative_base()


class TwitterAccountTable(base):
    __tablename__ = TWITTER_ACCOUNTS

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer)
    name = Column(String(15))
    user_name = Column(String(50))
    created_at = Column(DATETIME)
    updated_at = Column(DATETIME)

    def __repr__(self):
        return f"TwitterAccount(\
                id={self.id!r}, account_id={self.account_id!r}, name={self.name!r}, user_name={self.user_name!r}\
                created={self.created_at!r}, updated_at={self.updated_at!r}\
            )"
