import logging

import pymysql
import sqlalchemy
from sqlalchemy.pool import QueuePool

from libs.infrastractures.schemas import Base
from libs.infrastractures.twitter_account_repository import TwitterAccountRepository
from libs.response import *
from libs.services.collector import TwitterCollector
from libs.twitter_v2 import TwitterV2

logger = logging.getLogger('uvicorn')
env = Environment()
app = FastAPI()
twitter_v2_cli = TwitterV2(
    env.bearer_token,
    env.consumer_key, env.consumer_secret,
    env.access_token, env.access_token_secret,
    logger
)

engine = sqlalchemy.create_engine(
    # mysql+pymysql://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
    sqlalchemy.engine.url.URL.create(
        drivername="mysql+pymysql",
        username=env.db_user,
        password=env.db_pass,
        database=env.db_name,
        host=env.host,
        port=env.port,
    ),
    # 複数のリポジトリで使い回すので多めにコネクションをプールできるようにする
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
Base.metadata.create_all(engine)


try:
    twitter_db_cli = TwitterAccountRepository(engine, logger)

    twitter_svc = TwitterCollector(twitter_db_cli, twitter_v2_cli)

    @app.get("/accounts",
             response_model=AccountsReply,
             )
    async def list_accounts():
        resp = twitter_svc.list_accounts()
        res = [Account(account_id=r.account_id, name=r.name, user_name=r.user_name) for r in resp]
        return AccountsReply(result=res)


    @app.get("/accounts/me",
             response_model=AccountReply,
             responses={401: {"model": ErrorReply}, 500: {"model": ErrorReply}}
             )
    async def get_account():
        resp = twitter_v2_cli.get_me()
        return AccountReply(result=Account(account_id=resp.account_id, name=resp.name, user_name=resp.user_name))


    @app.get("/accounts/{account_id}",
             response_model=AccountReply,
             responses={401: {"model": ErrorReply}, 500: {"model": ErrorReply}}
             )
    async def get_account(account_id: int):
        resp = twitter_svc.get_account(account_id)
        return AccountReply(result=Account(account_id=resp.account_id, name=resp.name, user_name=resp.user_name))


    @app.put("/account/{id}",
             response_model=AccountReply,
             responses={401: {"model": ErrorReply}, 500: {"model": ErrorReply}}
             )
    async def update_account(account_id: int):
        resp = twitter_svc.update_account(account_id)
        return AccountReply(result=Account(account_id=resp.account_id, name=resp.name, user_name=resp.user_name))

    @app.get("/trends")
    async def list_trends():
        resp = twitter_svc.list_trends()
        return TwitterTrendsReply(
            result=[
                TwitterTrend(
                    name=r.name,
                    url=r.url,
                    query=r.query,
                    tweet_volue=r.tweet_volume
                ) for r in resp
            ]
        )

    app.add_middleware(HttpErrorMiddleware)

# DBコネクションの切断などで切れた場合に捕捉するコード
# TODO logging後にシャットダウンして通知しないと気づかない
except sqlalchemy.exc.OperationalError as e:
    logging.fatal(e)
except pymysql.err.OperationalError as e:
    logging.fatal(e)
