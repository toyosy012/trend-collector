import sqlalchemy
import sqlalchemy.pool as pool
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from typing import List
from .schemas import TwitterAccountTable
from ..services.accessor import DBAccessor
from ..models.twitter import TwitterAccount


# https://cloud.google.com/sql/docs/mysql/manage-connections?hl=ja


class TwitterRepository(DBAccessor):
    engine: sqlalchemy.engine.base.Engine
    pool: sqlalchemy.pool.QueuePool

    def __init__(self, db_user: str, db_pass: str, db_name: str, host: str, port: int):
        self.engine = sqlalchemy.create_engine(
            # postgresql+pg8000://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
            sqlalchemy.engine.url.URL.create(
                drivername="mysql+pymysql",
                username=db_user,
                password=db_pass,
                database=db_name,
                host=host,
                port=port,
            )
        )
        self.pool = pool.QueuePool(self.engine.connect(), max_overflow=10, pool_size=5)
        self.session_factory = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_me(self) -> TwitterAccount:
        return TwitterAccount()

    def update_me(self, twitter_account: TwitterAccount) -> TwitterAccount:
        return TwitterAccount()

    def list_accounts(self) -> List[TwitterAccount]:
        session = scoped_session(self.session_factory)
        rows = session.query(TwitterAccountTable)
        accounts = [TwitterAccount(account_id=r.account_id, name=r.name, user_name=r.user_name) for r in rows]
        return accounts

    def update_account(self, account: TwitterAccount) -> TwitterAccount:
        return TwitterAccount()

    def get_account(self, account_id: int) -> TwitterAccount:
        return TwitterAccount()
