import json
from abc import ABC, abstractmethod
from typing import Sequence

from . import RabbitMQClient


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


class QueryBuilder:
    __query_type: str
    __query_paths: Sequence[str]
    __query_data: dict

    def data(self, data: dict):
        self.__query_data = data
        return self

    def query_type(self, query_type: str):
        self.__query_type = query_type
        return self

    def paths(self, paths: Sequence[str]):
        self.__query_paths = paths
        return self

    def build(self):
        return {
            'Size': lambda paths, data: SizeQuery(paths, data)
            # 'Color': lambda paths, data: SimpleQuery(paths, data, "a")
            # 'Dogs'
        }[self.__query_type](self.__query_paths, self.__query_data)


class QueryExecutor:
    def __init__(self, producer: RabbitMQClient.RabbitMQProducer, consumer: RabbitMQClient.RabbitMQSyncConsumer):
        self.__producer = producer
        self.__consumer = consumer

    def execute(self, queries: Sequence[Query], query_cb):
        new_paths = queries[0].paths

        def callback(ch, method, properties, body):
            self.__consumer.stop_consuming()
            nonlocal current_query
            query_cb(body, current_query)
            nonlocal new_paths
            new_paths = json.loads(body)["paths"]

        current_query = 1
        for query in queries:
            query.paths = new_paths
            print(f"sent {query.json()} to {query.topic()} @ {query.exchange()}")
            self.__producer.publish(query.exchange(), query.topic(), query.json())

            self.__consumer.consume(callback)
            # if GLOBAL_EXECUTE_STOP: break
            current_query += 1
