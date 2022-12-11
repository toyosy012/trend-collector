from ..services.accessor import DBAccessor
from ..models.twitter import TwitterAccount


class TwitterDB(DBAccessor):

    def update_me(self) -> TwitterAccount: pass
