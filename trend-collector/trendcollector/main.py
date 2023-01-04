import uvicorn
from fastapi import APIRouter, FastAPI
from injector import Injector

from libs.infrastructures import (LoggingInjector,
                                  MediaCollectorDependenciesInjector,
                                  ORMEngineInjector,
                                  TwitterAccountDependenciesInjector,
                                  TwitterAuthInjector, bind_env,
                                  create_media_collector,
                                  create_twitter_account_binder)
from libs.infrastructures.api.v1.endpoints import (TrendRoutes,
                                                   TwitterAccountRoutes)
from libs.infrastructures.client.twitter_v2 import TwitterV2
from libs.infrastructures.logger import LogCustomizer
from libs.infrastructures.repositories import (TrendRepository,
                                               TwitterAccountRepository)
from libs.infrastructures.response import (AccountReply, AccountsReply,
                                           DeleteTrend, ErrorReply,
                                           HttpErrorMiddleware,
                                           TrendCommandResult, TrendMetrics,
                                           TrendSummaries, TrendSummary)
from libs.services.account import TwitterAccountService
from libs.services.collector import TwitterCollector

app = FastAPI()

orm_injector = Injector([bind_env, ORMEngineInjector()])
twitter_tokens_injector = Injector([bind_env, TwitterAuthInjector])

twitter_account_binder = create_twitter_account_binder(
    orm_injector.get(TwitterAccountRepository),
    twitter_tokens_injector.get(TwitterV2),
)
twitter_account_injector = Injector([twitter_account_binder, TwitterAccountDependenciesInjector()])
twitter_account_svc = twitter_account_injector.get(TwitterAccountService)

media_collector_binder = create_media_collector(
    orm_injector.get(TrendRepository),
    twitter_tokens_injector.get(TwitterV2)
)
media_injector = Injector([media_collector_binder, MediaCollectorDependenciesInjector()])
twitter_collector_svc = media_injector.get(TwitterCollector)

twitter_account_v1_routes = TwitterAccountRoutes(twitter_account_svc)
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
app.include_router(twitter_account_prefix, prefix="/v1")

trend_router = APIRouter()
trend_v1_routes = TrendRoutes(twitter_collector_svc)
trend_router.add_api_route("", trend_v1_routes.list_trend, methods=["GET"], response_model=TrendSummaries)
trend_router.add_api_route("", trend_v1_routes.insert_trend, methods=["POST"], response_model=TrendCommandResult,
                           responses={500: {"model": ErrorReply}})
trend_router.add_api_route("/{_id}", trend_v1_routes.get_trend, methods=["GET"], response_model=TrendSummary)
trend_router.add_api_route("/{_id}", trend_v1_routes.delete_trend, methods=["DELETE"], response_model=DeleteTrend,
                           responses={500: {"model": ErrorReply}})
trend_router.add_api_route("/metrics/{_id}", trend_v1_routes.list_trend_metrics, methods=["GET"],
                           response_model=TrendMetrics, responses={500: {"model": ErrorReply}})
trend_prefix = APIRouter()
trend_prefix.include_router(trend_router, prefix="/trends")
app.include_router(trend_prefix, prefix="/v1")

# config middlewares
logging_injector = Injector([bind_env, LoggingInjector()])
logger = logging_injector.get(LogCustomizer)
HttpLoggingHandler = logger.create_logging_handler()
app.add_middleware(HttpLoggingHandler)
app.add_middleware(HttpErrorMiddleware)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
