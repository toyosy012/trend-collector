import sqlalchemy

from http import HTTPStatus
from logging import Logger
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.orm.exc import DetachedInstanceError
from typing import List

from .schemas import TwitterAccountTable
from ..services import CustomException, DBAccessor
from ..models.twitter import TwitterAccount

# https://cloud.google.com/sql/docs/mysql/manage-connections?hl=ja


TWITTER_ACCOUNTS = "twitter_accounts"
FAILED_FETCH_ACCOUNT = "アカウントの取得に失敗"
FAILED_UPDATE_ACCOUNT = "アカウントの更新に失敗"
FAILED_FETCH_ACCOUNTS = "アカウントリストの取得に失敗"


class DetachedInstance(CustomException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


class OperationalException(CustomException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


class RuntimeException(CustomException):
    def __init__(self, code: int, message: str, details: list[str]):
        super().__init__(code, message, details)


class TwitterAccountRepository(DBAccessor):
    engine: Engine
    logger: Logger

    def __init__(self, engine: Engine, logger: Logger):
        self.engine = engine
        self.session = scoped_session(sessionmaker(autocommit=True, autoflush=True, bind=self.engine))
        self.logger = logger

    def list_accounts(self) -> List[TwitterAccount]:
        session: Session = self.session()
        try:
            rows = session.query(TwitterAccountTable).all()
        # DBダウン中にアクセスすると生じる
        except sqlalchemy.exc.OperationalError as e:
            self.logger.error(e)
            raise OperationalException(HTTPStatus.INTERNAL_SERVER_ERROR, FAILED_FETCH_ACCOUNTS, list(e.args))
        # DBダウン後にAPI再起動せずにアクセスすると生じる
        except RuntimeError as e:
            self.logger.error(e)
            raise RuntimeException(HTTPStatus.INTERNAL_SERVER_ERROR, FAILED_FETCH_ACCOUNTS, list(e.args))
        finally:
            session.close()
        return [
            TwitterAccount(user_id=r.id, account_id=r.account_id, name=r.name, user_name=r.user_name) for r in rows
        ]

    def update_account(self, new: TwitterAccount) -> TwitterAccount:
        session: Session = self.session()
        try:
            record = session.query(TwitterAccountTable).filter(TwitterAccountTable.account_id == new.account_id).first()
            record.name = new.name
            record.user_name = new.user_name
            session.add(record)
            n: TwitterAccount = self.get_account(new.user_id)
        except DetachedInstanceError as e:
            session.rollback()
            self.logger.error(e)
            raise DetachedInstance(HTTPStatus.INTERNAL_SERVER_ERROR, FAILED_UPDATE_ACCOUNT, list(e.args))
        except sqlalchemy.exc.OperationalError as e:
            session.rollback()
            self.logger.error(e)
            raise OperationalException(HTTPStatus.INTERNAL_SERVER_ERROR, FAILED_UPDATE_ACCOUNT, list(e.args))
        except RuntimeError as e:
            session.rollback()
            self.logger.error(e)
            raise RuntimeException(HTTPStatus.INTERNAL_SERVER_ERROR, FAILED_UPDATE_ACCOUNT, list(e.args))
        finally:
            session.close()
        return TwitterAccount(n.user_id, n.account_id, n.name, n.user_name)

    def get_account(self, user_id: int) -> TwitterAccount:
        session: Session = self.session()
        try:
            record = session.query(TwitterAccountTable).filter(
                TwitterAccountTable.id == user_id).first()
        except DetachedInstanceError as e:
            session.rollback()
            self.logger.error(e)
            raise DetachedInstance(HTTPStatus.INTERNAL_SERVER_ERROR, FAILED_FETCH_ACCOUNT, list(e.args))
        except sqlalchemy.exc.OperationalError as e:
            session.rollback()
            self.logger.error(e)
            raise OperationalException(HTTPStatus.INTERNAL_SERVER_ERROR, FAILED_FETCH_ACCOUNT, list(e.args))
        except RuntimeError as e:
            session.rollback()
            self.logger.error(e)
            raise RuntimeException(HTTPStatus.INTERNAL_SERVER_ERROR, FAILED_FETCH_ACCOUNT, list(e.args))
        finally:
            session.close()
        return TwitterAccount(record.id, record.account_id, record.name, record.user_name)
