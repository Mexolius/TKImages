import json
from abc import ABC, abstractmethod
from typing import Sequence

from RabbitMQClient import RabbitMQProducer


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
        self.path_number = len(paths)
        self.paths = paths
        self.param_number = len(params)
        self.params = params


class ResultResponse(RabbitMQMessage):
    def __init__(self, result, data, sender):
        self.result = result
        self.data = data
        self.total = len(data)
        self.sender = sender

    def topic(self):
        return 'results'


class SimpleQuery(Query):
    def __init__(self, paths: Sequence[str], data, moreData):
        params = {"data": data, "moreData": moreData}
        super().__init__(paths, params)

    def topic(self):
        return 'size'


class QueryExecutor:
    def __init__(self, producer: RabbitMQProducer):
        self.__producer = producer

    def execute(self, queries: Sequence[Query]):
        for q in queries:
            print(f"sent {q.json()} to {q.topic()} @ {q.exchange()}")
            self.__producer.publish(q.exchange(), q.topic(), q.json())
