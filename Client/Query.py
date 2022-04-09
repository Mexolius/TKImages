import json
from abc import ABC, abstractmethod
from typing import Sequence


class RabbitMQMessage(ABC):
    def exchange(self):
        return 'ImageFinder'

    @abstractmethod
    def topic(self):
        pass

    def json(self):
        return json.dumps(self.__dict__)


class Query(RabbitMQMessage, ABC):
    def __init__(self, paths: Sequence[str], params):
        params = {k: v for k, v in params.items() if v is not None and v != ""}
        self.path_number = len(paths)
        self.paths = paths
        self.param_number = len(params)
        self.params = params


class ResultResponse(RabbitMQMessage):
    def __init__(self, result, paths, sender):
        self.result = result
        self.paths = paths
        self.total = len(paths)
        self.sender = sender

    def topic(self):
        return 'results'


class SizeQuery(Query):
    def __init__(self, paths, params):
        super().__init__(paths, params)

    def topic(self):
        return 'size'


class SimpleQuery(Query):
    def __init__(self, paths: Sequence[str], data, moreData):
        params = {"data": data, "moreData": moreData}
        super().__init__(paths, params)

    def topic(self):
        return 'size'
