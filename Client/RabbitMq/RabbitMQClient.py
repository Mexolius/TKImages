import threading
from configparser import ConfigParser, ExtendedInterpolation

import pika

from abc import ABC, abstractmethod

from .Query import RabbitMQMessage


class RabbitMQConnection(ABC):
    _connection: pika.BlockingConnection
    _channel: pika.adapters.blocking_connection.BlockingChannel

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._connection:
            self._connection.close()

    def __del__(self):
        if self._connection:
            self._connection.close()


class RabbitMQProducer(RabbitMQConnection):
    @staticmethod
    def from_config():
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read('config.ini')
        rabbit = config['RABBITMQ']

        return RabbitMQProducer(
            rabbit.get('address'),
            rabbit.get('port'),
            rabbit.get('username'),
            rabbit.get('password'),
        )

    def __init__(self, server, port, username, password):
        params = pika.ConnectionParameters(server, credentials=pika.PlainCredentials(username, password), port=port)
        self._connection = pika.BlockingConnection(params)
        self._channel = self._connection.channel()

    def publish(self, exchange, topic, data):
        self._channel.basic_publish(exchange=exchange, routing_key=topic, body=data)

    def publish_rmq_message(self, message: RabbitMQMessage):
        self._channel.basic_publish(exchange=message.exchange(), routing_key=message.topic(), body=message.json())


class RabbitMQConsumer(RabbitMQConnection, ABC):
    _exchange: str
    _queue: str

    @staticmethod
    def from_config(queue_name: str):
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read('config.ini')
        rabbit = config['RABBITMQ']

        return RabbitMQSyncConsumer(
            rabbit.get('address'),
            rabbit.get('port'),
            rabbit.get('exchange'),
            config.get('QUEUES', queue_name),
            rabbit.get('username'),
            rabbit.get('password'),
        )

    def __init__(self, server, port, exchange, queue, username, password):
        params = pika.ConnectionParameters(server, credentials=pika.PlainCredentials(username, password), port=port)
        self._connection = pika.BlockingConnection(params)
        self._channel = self._connection.channel()
        self._exchange = exchange
        self._queue = queue

    def stop_consuming(self):
        self._channel.stop_consuming()

    @abstractmethod
    def consume(self, callback): ...


class RabbitMQSyncConsumer(RabbitMQConsumer):

    def consume(self, callback):
        self._channel.basic_consume(queue=self._queue, on_message_callback=callback, auto_ack=True)
        self._channel.start_consuming()


class RabbitMQAsyncConsumer(RabbitMQConsumer, RabbitMQConnection):

    def consume(self, callback):
        self._channel.basic_consume(
            queue=self._queue,
            on_message_callback=callback,
            auto_ack=True)

        def start_self():
            self._channel.start_consuming()

        consumer_thread = threading.Thread(target=start_self)
        consumer_thread.start()
