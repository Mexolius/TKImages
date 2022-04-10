import threading
from configparser import ConfigParser, ExtendedInterpolation

import pika

from abc import ABC, abstractmethod

from .Query import RabbitMQMessage


class RabbitMQConnection(ABC):
    __connection: pika.BlockingConnection
    __channel: pika.adapters.blocking_connection.BlockingChannel

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.__connection:
            self.__connection.close()

    def __del__(self):
        if self.__connection:
            self.__connection.close()


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
        self.__connection = pika.BlockingConnection(params)
        self.__channel = self.__connection.channel()

    def publish(self, exchange, topic, data):
        self.__channel.basic_publish(exchange=exchange, routing_key=topic, body=data)

    def publish_rmq_message(self, message: RabbitMQMessage):
        self.__channel.basic_publish(exchange=message.exchange(), routing_key=message.topic(), body=message.json())


class RabbitMQConsumer(RabbitMQConnection, ABC):
    __exchange: str
    __queue: str

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
        self.__connection = pika.BlockingConnection(params)
        self.__channel = self.__connection.channel()
        self.__exchange = exchange
        self.__queue = queue

    def stop_consuming(self):
        self.__channel.stop_consuming()

    @abstractmethod
    def consume(self, callback): ...


class RabbitMQSyncConsumer(RabbitMQConsumer):

    def consume(self, callback):
        self.__channel.basic_consume(queue=self.__queue, on_message_callback=callback, auto_ack=True)
        self.__channel.start_consuming()


class RabbitMQAsyncConsumer(RabbitMQConsumer):

    def consume(self, callback):
        self.__channel.basic_consume(
            queue=self.__queue,
            on_message_callback=callback,
            auto_ack=True)

        def start_self():
            self.__channel.start_consuming()

        consumer_thread = threading.Thread(target=start_self)
        consumer_thread.start()
