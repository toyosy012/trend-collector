import logging
from typing import Union

import sqlalchemy
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.pool import QueuePool

from libs.infrastractures.repositories.schemas import Base
from libs.infrastractures import TrendRepository, TwitterAccountRepository
from libs.infrastractures.response import *
from libs.infrastractures.client.twitter_v2 import TwitterV2
from libs.services.collector import TwitterCollector


env = Environment()
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
twitter_v2_cli = TwitterV2(
    env.bearer_token,
    env.consumer_key, env.consumer_secret,
    env.access_token, env.access_token_secret,
)


try:
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

    trend_repo = TrendRepository(engine)
    twitter_account_repo = TwitterAccountRepository(engine)

    twitter_svc = TwitterCollector(trend_repo, twitter_account_repo, twitter_v2_cli)

    @app.get("/accounts", response_model=AccountsReply)
    async def list_accounts():
        resp = twitter_svc.list_accounts()
        res = [Account(id=r.id, account_id=r.account_id, name=r.name, user_name=r.display_name) for r in resp]
        return AccountsReply(result=res)

    @app.get("/auth", response_model=Token)
    async def auth(token: str = Depends(oauth2_scheme)) -> Token:
        return Token(token=token)

    @app.get("/accounts/me",
             response_model=AccountReply,
             responses={401: {"model": ErrorReply}, 500: {"model": ErrorReply}}
             )
    async def get_my_account():
        resp = twitter_v2_cli.get_me()
        return AccountReply(
            result=Account(id=resp.id, account_id=resp.account_id, name=resp.name, user_name=resp.display_name))

    @app.get("/accounts/{_id}",
             response_model=AccountReply,
             responses={401: {"model": ErrorReply}, 404: {"model": ErrorReply}, 500: {"model": ErrorReply}}
             )
    async def get_account(_id: int):
        resp = twitter_svc.get_account(_id)
        return AccountReply(
            result=Account(id=resp.id, account_id=resp.account_id, name=resp.name, user_name=resp.display_name))

    @app.get("/update/{_id}",
             response_model=AccountReply,
             responses={401: {"model": ErrorReply}, 500: {"model": ErrorReply}}
             )
    async def update_account(_id: int):
        resp = twitter_svc.update_account(_id)
        return AccountReply(
            result=Account(id=resp.id, account_id=resp.account_id, name=resp.name, user_name=resp.display_name))

    @app.get("/update/trends/{woeid}", response_model=UpsertTrends, responses={500: {"model": ErrorReply}})
    async def collect_current_trends(woeid: int):
        resp = twitter_svc.upsert_trends(woeid)
        return UpsertTrends(success=resp)

    @app.get("/trends/{_id}", response_model=TwitterTrend)
    async def get_trend(_id: int):
        resp = twitter_svc.get_trend(_id)
        return TwitterTrend(id=resp.id, name=resp.name, query=resp.query, tweet_volume=resp.tweet_volume)

    @app.get("/trends", response_model=TwitterTrendsReply)
    async def list_trend(page: Union[int, None] = 1, counts: Union[int, None] = 20):
        resp = twitter_svc.list_trends(page, counts)
        return TwitterTrendsReply(
            result=[TwitterTrend(id=t.id, name=t.name, query=t.query, tweet_volume=t.tweet_volume) for t in resp],
            length=len(resp)
        )

    @app.delete("/trends/{_id}", response_model=DeleteTrends)
    async def delete_trend(_id: int):
        resp = twitter_svc.delete_trend(_id)
        return DeleteTrends(success=resp)

    app.add_middleware(HttpErrorMiddleware)

# DBコネクションの切断などで切れた場合に捕捉するコード
# TODO logging後にシャットダウンして通知しないと気づかない
except ConnectionRefusedError as e:
    logging.fatal(e)
except sqlalchemy.exc.OperationalError as e:
    logging.fatal(e)
except RuntimeError as e:
    logging.fatal(e)
