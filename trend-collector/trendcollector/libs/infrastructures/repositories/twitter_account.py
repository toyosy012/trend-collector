from http import HTTPStatus
from logging import Logger

from injector import inject, singleton
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import NoResultFound, OperationalError
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from ...models.twitter import TwitterAccount
from ...services.accessor import TwitterAccountAccessor
from ...services.custom_exception import DisconnectionDB, NoTwitterAccountRecord, SEARCH_ERROR, UPDATE_ERROR
from ..repositories.schemas import TwitterAccountTable

# https://cloud.google.com/sql/docs/mysql/manage-connections?hl=ja

FAILED_FETCH_ACCOUNT = "Twitterアカウントデータの取得に失敗"
FAILED_FETCH_ACCOUNTS = "Twitterアカウントリストデータは取得に失敗"
FAILED_UPDATE_ACCOUNT = "Twitterアカウントデータの更新に失敗"


@singleton
class TwitterAccountRepository(TwitterAccountAccessor):
    engine: Engine
    logger: Logger

    @inject
    def __init__(self, engine: Engine):
        self.engine = engine
        self.session_factory = scoped_session(sessionmaker(autocommit=True, autoflush=True, bind=self.engine))

    def list_accounts(self) -> [TwitterAccount]:
        session: Session = self.session_factory()
        try:
            rows = session.query(TwitterAccountTable).all()
        except OperationalError as e:
            raise DisconnectionDB(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                f"{SEARCH_ERROR}: {FAILED_FETCH_ACCOUNTS}", list(e.args)
            )
        finally:
            session.close()
        return [
            TwitterAccount(_id=r.id, account_id=r.account_id, name=r.name, display_name=r.display_name) for r in rows
        ]

    def update_account(self, new: TwitterAccount) -> TwitterAccount:
        session: Session = self.session_factory()
        try:
            session.begin()

            record = session.query(
                TwitterAccountTable).filter(TwitterAccountTable.account_id == new.account_id).one()
            record.name = new.name
            record.display_name = new.display_name
            session.add(record)
            session.commit()
            n: TwitterAccount = self.get_account(record.id)
        except NoResultFound as e:
            raise NoTwitterAccountRecord(
                HTTPStatus.BAD_REQUEST, UPDATE_ERROR, list(e.args)
            )
        except OperationalError as e:
            raise DisconnectionDB(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                f"{UPDATE_ERROR}: {FAILED_UPDATE_ACCOUNT}", list(e.args)
            )
        finally:
            session.close()
        return TwitterAccount(n.id, n.account_id, n.name, n.display_name)

    def get_account(self, _id: int) -> TwitterAccount:
        session: Session = self.session_factory()
        try:
            record = session.query(TwitterAccountTable).filter(TwitterAccountTable.id == _id).one()
            return TwitterAccount(record.id, record.account_id, record.name, record.display_name)
        except NoResultFound as e:
            raise NoTwitterAccountRecord(
                HTTPStatus.BAD_REQUEST, SEARCH_ERROR, list(e.args)
            )
        except OperationalError as e:
            raise DisconnectionDB(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"{SEARCH_ERROR}: {FAILED_FETCH_ACCOUNT}", list(e.args)
            )
        finally:
            session.close()
