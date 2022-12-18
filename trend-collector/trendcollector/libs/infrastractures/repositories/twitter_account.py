from logging import Logger

from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from ...models.twitter import TwitterAccount
from ...services.accessor import TwitterAccountAccessor
from ..repositories.schemas import TwitterAccountTable, handle_exception

# https://cloud.google.com/sql/docs/mysql/manage-connections?hl=ja


class TwitterAccountRepository(TwitterAccountAccessor):
    engine: Engine
    logger: Logger

    def __init__(self, engine: Engine, logger: Logger):
        self.engine = engine
        self.session = scoped_session(sessionmaker(autocommit=True, autoflush=True, bind=self.engine))
        self.logger = logger

    @handle_exception
    def list_accounts(self) -> [TwitterAccount]:
        session: Session = self.session()
        try:
            rows = session.query(TwitterAccountTable).all()
        except Exception as e:
            raise e
        finally:
            session.close()
        return [
            TwitterAccount(_id=r.id, account_id=r.account_id, name=r.name, display_name=r.display_name) for r in rows
        ]

    @handle_exception
    def update_account(self, new: TwitterAccount) -> TwitterAccount:
        session: Session = self.session()
        try:
            record = session.query(TwitterAccountTable).filter(TwitterAccountTable.account_id == new.account_id).first()
            record.name = new.name
            record.display_name = new.display_name
            session.add(record)
            n: TwitterAccount = self.get_account(new.id)
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        return TwitterAccount(n.id, n.account_id, n.name, n.display_name)

    @handle_exception
    def get_account(self, _id: int) -> TwitterAccount:
        session: Session = self.session()
        try:
            record = session.query(TwitterAccountTable).filter(TwitterAccountTable.id == _id).first()
            return TwitterAccount(record.id, record.account_id, record.name, record.display_name)
        except Exception as e:
            raise e
        finally:
            session.close()
