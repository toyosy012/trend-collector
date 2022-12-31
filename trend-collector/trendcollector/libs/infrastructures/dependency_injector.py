import logging
import sys
from typing import Callable

import sqlalchemy.engine
from injector import Binder, Module, provider, singleton
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import QueuePool

from .conf import Environment
from ..services import TrendAccessor, Twitter, TwitterAccountAccessor


class Authentications:
    def __init__(
            self,
            bearer_token: str,
            consumer_key: str,
            consumer_secret: str,
            access_token: str,
            access_token_secret: str
    ):
        self.bearer_token = bearer_token
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret


def bind_env(binder: Binder):
    env = Environment()
    binder.bind(Environment, env)
    binder.bind(
        Authentications,
        Authentications(
            env.bearer_token,
            env.consumer_key,
            env.consumer_secret,
            env.access_token,
            env.access_token_secret
        )
    )


def create_media_collector(
        trend_accessor: TrendAccessor, twitter_account_accessor: TwitterAccountAccessor, twitter: Twitter
) -> Callable[[Binder], None]:
    def _bind_media_collector(binder: Binder) -> None:
        binder.bind(TrendAccessor, trend_accessor)
        binder.bind(TwitterAccountAccessor, twitter_account_accessor)
        binder.bind(Twitter, twitter)

    return _bind_media_collector


class TwitterAuthInjector(Module):
    @singleton
    @provider
    def provide(self, env: Environment) -> Authentications:
        return Authentications(
            env.bearer_token, env.consumer_key, env.consumer_secret, env.access_token, env.access_token_secret)


class ORMEngineInjector(Module):
    @singleton
    @provider
    def provide_engine(self, env: Environment) -> Engine:
        try:
            return sqlalchemy.create_engine(
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
        # DBコネクションの切断などで切れた場合に捕捉するコード
        except ConnectionRefusedError as e:
            logging.fatal(e)
            sys.exit(1)
        except OperationalError as e:
            logging.fatal(e)
            sys.exit(1)
        except RuntimeError as e:
            logging.fatal(e)
            sys.exit(1)


class LoggingInjector(Module):
    @singleton
    @provider
    def provide_output_path(self, env: Environment) -> str:
        return env.result_log


class MediaCollectorDependenciesInjector(Module):
    @singleton
    @provider
    def provide(
            self,
            trend_accessor: TrendAccessor,
            twitter_account_binder: TwitterAccountAccessor,
            twitter: Twitter
    ) -> (TrendAccessor, TwitterAccountAccessor, Twitter):
        return trend_accessor, twitter_account_binder, twitter
