from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from libs.conf import Environment
from libs.twitter_v2 import TwitterV2
from libs.response import HttpErrorMiddleware


env = Environment()
app = FastAPI()
twitter_v2_cli = TwitterV2(
    env.bearer_token,
    env.consumer_key, env.consumer_secret,
    env.access_token, env.access_token_secret
)


@app.get("/")
async def root():
    resp = twitter_v2_cli.get_me()
    return {"result": jsonable_encoder(resp)}

app.add_middleware(HttpErrorMiddleware)
