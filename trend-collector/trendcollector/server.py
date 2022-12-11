from fastapi import FastAPI
from libs.conf import Environment
from libs.infrastractures.database import TwitterRepository
from libs.services.collector import TwitterCollector
from libs.twitter_v2 import TwitterV2
from libs.response import Account, AccountReply, AccountsReply, ErrorReply, HttpErrorMiddleware

env = Environment()
app = FastAPI()
twitter_v2_cli = TwitterV2(
    env.bearer_token,
    env.consumer_key, env.consumer_secret,
    env.access_token, env.access_token_secret
)



twitter_db_cli = TwitterRepository(env.db_user, env.db_pass, env.db_name, env.host, env.port)

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
async def root():
    resp = twitter_v2_cli.get_me()
    return AccountReply(result=Account(account_id=resp.account_id, name=resp.name, user_name=resp.user_name))


app.add_middleware(HttpErrorMiddleware)
