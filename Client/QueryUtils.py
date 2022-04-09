import json

from typing import Sequence
from Query import SizeQuery, Query
from Color import ColorQuery
from RabbitMQClient import RabbitMQProducer, RabbitMQSyncConsumer


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
            'Size': lambda paths, data: SizeQuery(paths, data),
            'Colors': lambda paths, data: ColorQuery(paths, data)
            # 'Dogs'
        }[self.__query_type](self.__query_paths, self.__query_data)


class QueryExecutor:
    def __init__(self, producer: RabbitMQProducer, consumer: RabbitMQSyncConsumer):
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