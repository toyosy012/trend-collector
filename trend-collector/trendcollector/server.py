from fastapi import FastAPI
from libs.conf import Environment
from libs.twitter_v2 import TwitterV2
from libs.response import Account, ErrorReply, HttpErrorMiddleware, AccountReply

env = Environment()
app = FastAPI()
twitter_v2_cli = TwitterV2(
    env.bearer_token,
    env.consumer_key, env.consumer_secret,
    env.access_token, env.access_token_secret
)


@app.get("/accounts/me",
         response_model=AccountReply,
         responses={401: {"model": ErrorReply}, 500: {"model": ErrorReply}}
         )
async def root():
    resp = twitter_v2_cli.get_me()
    return AccountReply(result=Account(account_id=resp.account_id, name=resp.name, user_name=resp.user_name))


app.add_middleware(HttpErrorMiddleware)
