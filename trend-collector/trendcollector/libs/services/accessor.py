import abc

from ..models.twitter import TwitterAccount


class DBAccessor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def update_me(self) -> TwitterAccount: pass
