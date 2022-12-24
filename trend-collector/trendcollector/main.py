import logging
import sys

import sqlalchemy
import uvicorn
from fastapi import APIRouter, Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.pool import QueuePool

from libs.infrastructures import TrendRepository, TwitterAccountRepository
from libs.infrastructures.api.v1.endpoints import TrendRoutes, TwitterAccountRoutes
from libs.infrastructures.client.twitter_v2 import TwitterV2
from libs.infrastructures.logger import config_logger, create_logging_handler
from libs.infrastructures.repositories.schemas import Base
from libs.infrastructures.response import *
from libs.services.collector import TwitterCollector

env = Environment()

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
        max_overflow=20,
        pool_pre_ping=True
    )
    Base.metadata.create_all(engine)

# DBコネクションの切断などで切れた場合に捕捉するコード
# TODO logging後にシャットダウンして通知しないと気づかない
except ConnectionRefusedError as e:
    logging.fatal(e)
    sys.exit(1)
except sqlalchemy.exc.OperationalError as e:
    logging.fatal(e)
    sys.exit(1)
except RuntimeError as e:
    logging.fatal(e)
    sys.exit(1)


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
twitter_v2_cli = TwitterV2(
    env.bearer_token,
    env.consumer_key, env.consumer_secret,
    env.access_token, env.access_token_secret,
)
trend_repo = TrendRepository(engine)
twitter_account_repo = TwitterAccountRepository(engine)

twitter_svc = TwitterCollector(trend_repo, twitter_account_repo, twitter_v2_cli)
twitter_account_v1_routes = TwitterAccountRoutes(twitter_svc)

twitter_account_router = APIRouter()
twitter_account_router.add_api_route("", twitter_account_v1_routes.list_accounts, methods=["GET"],
                                     response_model=AccountsReply,
                                     responses={401: {"model": ErrorReply}, 500: {"model": ErrorReply}})
twitter_account_router.add_api_route("/me", twitter_account_v1_routes.get_my_account, methods=["GET"],
                                     response_model=AccountReply,
                                     responses={401: {"model": ErrorReply}, 500: {"model": ErrorReply}})
twitter_account_router.add_api_route("/update/me", twitter_account_v1_routes.update_my_account, methods=["GET"],
                                     response_model=AccountReply,
                                     responses={401: {"model": ErrorReply}, 500: {"model": ErrorReply}})
twitter_account_router.add_api_route("/{_id}", twitter_account_v1_routes.get_account,
                                     methods=["GET"], response_model=AccountReply,
                                     responses={
                                         401: {"model": ErrorReply}, 404: {"model": ErrorReply},
                                         500: {"model": ErrorReply}
                                     })
twitter_account_router.add_api_route("/update/{_id}", twitter_account_v1_routes.update_account,
                                     methods=["GET"], response_model=AccountReply,
                                     responses={
                                         401: {"model": ErrorReply}, 404: {"model": ErrorReply},
                                         500: {"model": ErrorReply}
                                     })
twitter_account_prefix = APIRouter()
twitter_account_prefix.include_router(twitter_account_router, prefix="/accounts")

trend_v1_routes = TrendRoutes(twitter_svc)
trend_router = APIRouter()
trend_router.add_api_route("", trend_v1_routes.list_trend, methods=["GET"], response_model=TwitterTrendsReply)
trend_router.add_api_route("/{_id}", trend_v1_routes.get_trend, methods=["GET"], response_model=TwitterTrend)
trend_router.add_api_route("/update/{woeid}", trend_v1_routes.collect_current_trends, methods=["GET"],
                           response_model=UpsertTrends, responses={500: {"model": ErrorReply}})
trend_router.add_api_route("/{_id}", trend_v1_routes.delete_trend, methods=["DELETE"], response_model=DeleteTrend,
                           responses={500: {"model": ErrorReply}})
trend_prefix = APIRouter()
trend_prefix.include_router(trend_router, prefix="/trends")

app.include_router(twitter_account_prefix, prefix="/v1")
app.include_router(trend_prefix, prefix="/v1")


@app.get("/auth", response_model=Token)
async def auth(token: str = Depends(oauth2_scheme)) -> Token:
    return Token(token=token)

# config middlewares
HttpLoggingHandler = create_logging_handler(config_logger(env.result_log))
app.add_middleware(HttpLoggingHandler)
app.add_middleware(HttpErrorMiddleware)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
