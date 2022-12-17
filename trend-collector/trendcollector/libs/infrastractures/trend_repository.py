import functools

from http import HTTPStatus
from logging import Logger
from sqlalchemy.dialects import mysql
from sqlalchemy.exc import OperationalError as SQLAlchemyOperationalError
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session

from .schemas import TrendTable
from ..models import Trend
from ..services.accessor import InvalidRequestException, TrendAccessor, OperationalException, FAILED_FETCH_TRENDS


# コールバック関数の引数(*args, **kwargs)をCallableで表現することは不可能なので型ヒントは書かない
def handle_exception(func):
    @functools.wraps(func)
    def _handler_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyOperationalError as e:
            raise OperationalException(HTTPStatus.INTERNAL_SERVER_ERROR, FAILED_FETCH_TRENDS, list(e.args))
        except InvalidRequestError as e:
            raise InvalidRequestException(HTTPStatus.INTERNAL_SERVER_ERROR, FAILED_FETCH_TRENDS, list(e.args))

    return _handler_wrapper


class TrendRepository(TrendAccessor):
    engine: Engine
    logger: Logger

    def __init__(self, engine: Engine, logger: Logger):
        self.engine = engine
        self.session_factory = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))
        self.logger = logger

    @handle_exception
    def get(self, _id: int) -> Trend:
        pass

    @handle_exception
    def list(self) -> [Trend]:
        pass

    @handle_exception
    def upsert(self, trends: [Trend]) -> bool:
        insert_stmt = mysql.insert(TrendTable).values([
            dict(
                name=t.name,
                query=t.query,
                tweet_volume=t.tweet_volume,
            )
            for t in trends
        ])
        upsert_stmt = insert_stmt.on_duplicate_key_update(
            tweet_volume=insert_stmt.inserted.tweet_volume,
        )

        session: Session = self.session_factory()
        try:
            session.execute(upsert_stmt)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @handle_exception
    def delete(self, _id: int) -> bool:
        pass
