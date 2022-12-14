from http import HTTPStatus
from logging import Logger
from typing import List

from injector import inject, singleton
from sqlalchemy.dialects import mysql
from sqlalchemy.engine import Engine
from sqlalchemy.exc import NoResultFound, OperationalError
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from ...models import InputRawTrend, TrendSummary
from ...services.accessor import TrendAccessor
from ...services.custom_exception import (DELETE_ERROR, SEARCH_ERROR,
                                          UPDATE_ERROR, DisconnectionDB,
                                          NoTrendRecord)
from .schemas import TrendTable

FAILED_DELETE_TREND = "トレンドデータの削除に失敗しました"
FAILED_FETCH_TREND = "トレンドデータは取得に失敗"
FAILED_FETCH_TRENDS = "トレンドリストデータは取得に失敗"
FAILED_UPDATE_TRENDS = "トレンドデータの更新に失敗"


@singleton
class TrendRepository(TrendAccessor):
    engine: Engine
    logger: Logger

    @inject
    def __init__(self, engine: Engine):
        self.engine = engine
        self.session_factory = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))

    def get(self, _id: int) -> TrendSummary:
        session = self.session_factory()
        try:
            trend = session.query(
                TrendTable.id, TrendTable.name, TrendTable.updated_at).filter(TrendTable.id == _id).one()

            return TrendSummary(_id=trend.id, name=trend.name, updated_at=trend.updated_at)

        except NoResultFound as e:
            raise NoTrendRecord(
                HTTPStatus.BAD_REQUEST, SEARCH_ERROR, list(e.args)
            ) from e
        except OperationalError as e:
            raise DisconnectionDB(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{SEARCH_ERROR}: {FAILED_FETCH_TREND}", list(e.args)
            ) from e
        finally:
            session.close()

    def list(self, page: int, counts: int) -> list[TrendSummary]:
        session: Session = self.session_factory()
        try:
            trends = session.query(TrendTable).offset((page - 1) * counts).limit(counts).all()

            return [
                TrendSummary(_id=t.id, name=t.name, updated_at=t.updated_at) for t in trends] if 0 < len(trends) else []
        except OperationalError as e:
            raise DisconnectionDB(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{SEARCH_ERROR}: {FAILED_FETCH_TRENDS}", list(e.args)
            ) from e
        finally:
            session.close()

    # Warning: when using `insert prefix_with IGNORE` & `auto_increment` together,
    # ID-like increments will increase rapidly!
    def insert_trends(self, trends: List[InputRawTrend]) -> bool:
        insert_stmt = mysql.insert(TrendTable).prefix_with('IGNORE').values([
            dict(
                name=t.name,
                query=t.query,
            )
            for t in trends
        ])

        session: Session = self.session_factory()
        try:
            session.execute(insert_stmt)
            session.commit()
            return True
        except OperationalError as e:
            session.rollback()
            raise DisconnectionDB(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{UPDATE_ERROR}: {FAILED_UPDATE_TRENDS}", list(e.args)
            ) from e
        finally:
            session.close()

    def delete(self, _id: int) -> bool:
        session: Session = self.session_factory()
        try:
            session.query(TrendTable).filter(TrendTable.id == _id).one()
            session.query(TrendTable).filter(TrendTable.id == _id).delete()
            session.commit()
            return True
        except NoResultFound as e:
            raise NoTrendRecord(
                HTTPStatus.BAD_REQUEST, DELETE_ERROR, list(e.args)
            ) from e
        except OperationalError as e:
            raise DisconnectionDB(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{DELETE_ERROR}: {FAILED_DELETE_TREND}", list(e.args)
            ) from e
        finally:
            session.close()
