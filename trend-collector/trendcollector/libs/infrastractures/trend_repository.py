from logging import Logger

from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .. import Trend, TwitterAccount
from ..services import TrendAccessor


class TwitterAccountRepository(TrendAccessor):
    engine: Engine
    logger: Logger

    def __init__(self, engine: Engine, logger: Logger):
        self.engine = engine
        self.session = scoped_session(sessionmaker(autocommit=True, autoflush=True, bind=self.engine))
        self.logger = logger

    def get(self, _id: int) -> TwitterAccount:
        pass

    def list(self) -> list[Trend]:
        pass

    def update(self, trend: Trend) -> Trend:
        pass

    def delete(self, _id: int) -> bool:
        pass

