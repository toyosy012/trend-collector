from sqlalchemy import Column, DATETIME, Integer, String
from sqlalchemy.ext.declarative import declarative_base


TWITTER_ACCOUNTS = "twitter_accounts"

Base = declarative_base()


class TwitterAccountTable(Base):
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


class TrendTable(Base):
    __tablename__ = "trends"

    id = Column(Integer, primary_key=True)
    name = Column(String(90))
    query = Column(String(270))  # 3バイト文字をurlエンコードすると9バイトになるとのことで3倍を設定
    tweet_volume = Column(Integer)
    created_at = Column(DATETIME)
    updated_at = Column(DATETIME)

    def __repr__(self):
        return f"TwitterAccount(\
                id={self.id!r}, name={self.name!r}, query={self.query!r}, tweet_volume={self.tweet_volume!r}\
                created_at={self.created_at!r}, updated_at={self.updated_at!r}\
            )"
