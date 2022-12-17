import functools

from http import HTTPStatus
from logging import Logger
from sqlalchemy.exc import OperationalError as SQLAlchemyOperationalError
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker

from ..models import Trend
from ..services.accessor import TrendAccessor, OperationalException, FAILED_UPDATE_ACCOUNT


# コールバック関数の引数(*args, **kwargs)をCallableで表現することは不可能なので型ヒントは書かない
def handle_exception(func):
    @functools.wraps(func)
    def _handler_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyOperationalError as e:
            raise OperationalException(HTTPStatus.INTERNAL_SERVER_ERROR, FAILED_UPDATE_ACCOUNT, list(e.args))

    return _handler_wrapper


class TwitterAccountRepository(TrendAccessor):
    engine: Engine
    logger: Logger

    def __init__(self, engine: Engine, logger: Logger):
        self.engine = engine
        self.session = scoped_session(sessionmaker(autocommit=True, autoflush=True, bind=self.engine))
        self.logger = logger

    @handle_exception
    def get(self, _id: int) -> Trend:
        pass

    @handle_exception
    def list(self) -> list[Trend]:
        pass

    @handle_exception
    def update(self, trend: Trend) -> Trend:
        pass

    @handle_exception
    def delete(self, _id: int) -> bool:
        pass
