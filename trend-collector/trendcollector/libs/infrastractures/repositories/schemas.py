import functools
import traceback
from http import HTTPStatus

from sqlalchemy import DATETIME, Column, String
from sqlalchemy.dialects.mysql import INTEGER as Integer
from sqlalchemy.exc import InvalidRequestError, OperationalError as SQLAlchemyOperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import DetachedInstanceError
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.functions import current_timestamp

from ..client.twitter_v2 import IntervalServerException, FAILED_GET_MY_ACCOUNT
from ...services.accessor import (AttributesException, DetachedInstance, InvalidRequestException,
                                  OperationalException, RuntimeException)


# コールバック関数の引数(*args, **kwargs)をCallableで表現することは不可能なので型ヒントは書かない
def handle_exception(func):
    @functools.wraps(func)
    def _handler_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DetachedInstanceError as e:
            raise DetachedInstance(HTTPStatus.INTERNAL_SERVER_ERROR, "", list(e.args), traceback.format_exc())
        except SQLAlchemyOperationalError as e:
            raise OperationalException(HTTPStatus.INTERNAL_SERVER_ERROR, "", list(e.args), traceback.format_exc())
        except InvalidRequestError as e:
            raise InvalidRequestException(HTTPStatus.INTERNAL_SERVER_ERROR, "", list(e.args), traceback.format_exc())
        except AttributeError as e:
            raise AttributesException(HTTPStatus.BAD_REQUEST, "", list(e.args), traceback.format_exc())
        except RuntimeError as e:
            raise RuntimeException(HTTPStatus.INTERNAL_SERVER_ERROR, "", list(e.args), traceback.format_exc())
        except Exception as e:
            raise IntervalServerException(
                HTTPStatus.INTERNAL_SERVER_ERROR, FAILED_GET_MY_ACCOUNT, list(e.args), traceback.format_exc())

    return _handler_wrapper


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
