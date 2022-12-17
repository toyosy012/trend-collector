import functools

from http import HTTPStatus
from logging import Logger
from sqlalchemy.dialects import mysql
from sqlalchemy.exc import OperationalError as SQLAlchemyOperationalError
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from typing import List

from .schemas import TrendTable
from ..models import Trend, WoeidRawTrend
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
        session = self.session_factory()
        try:
            record: TrendTable = session.query(TrendTable).filter(TrendTable.id == _id).first()
            return Trend(_id=record.id, name=record.name, query=record.query, tweet_volume=record.tweet_volume)
        except Exception as e:
            self.logger.error(e)
            raise e
        finally:
            session.close()

    @handle_exception
    def list(self, page: int, counts: int) -> list[Trend]:
        session: Session = self.session_factory()
        try:
            resp = session.query(TrendTable).offset((page - 1) * counts).limit(counts).all()
            return [Trend(_id=t.id, name=t.name, query=t.query, tweet_volume=t.tweet_volume) for t in resp]
        except Exception as e:
            raise e
        finally:
            session.close()

    @handle_exception
    def upsert(self, trends: List[WoeidRawTrend]) -> bool:
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
            self.logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

    @handle_exception
    def delete(self, _id: Trend) -> bool:
        session: Session = self.session_factory()
        try:
            session.query(TrendTable).filter(TrendTable.id == _id).delete()
            session.commit()
            return True
        except Exception as e:
            self.logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()
