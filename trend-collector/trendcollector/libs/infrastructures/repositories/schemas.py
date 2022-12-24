from sqlalchemy import DATETIME, Column, String
from sqlalchemy.dialects.mysql import INTEGER as Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.functions import current_timestamp


Base = declarative_base()


class TwitterAccountTable(Base):
    __tablename__ = "twitter_accounts"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer)
    name = Column(String(15))
    display_name = Column(String(50))
    created_at = Column(DATETIME)
    updated_at = Column(DATETIME)

    def __repr__(self):
        return f"TwitterAccount(\
                id={self.id!r}, account_id={self.account_id!r}, name={self.name!r}, user_name={self.display_name!r}\
                created={self.created_at!r}, updated_at={self.updated_at!r}\
            )"


class TrendTable(Base):
    __tablename__ = "trends"

    id = Column(Integer(unsigned=True), primary_key=True, unique=True, nullable=False)
    name = Column(String(120), unique=True, nullable=False)
    query = Column(String(360), unique=True, nullable=False)  # 4バイト文字をurlエンコードすると9バイトになるとのことで3倍を設定
    tweet_volume = Column(Integer(unsigned=True), nullable=False)
    created_at = Column(DATETIME, nullable=False, server_default=current_timestamp())
    updated_at = Column(DATETIME, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"TwitterAccount(\
                id={self.id!r}, name={self.name!r}, query={self.query!r}, tweet_volume={self.tweet_volume!r}\
                created_at={self.created_at!r}, updated_at={self.updated_at!r}\
            )"
