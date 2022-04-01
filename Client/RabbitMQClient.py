import threading

import pika


class RabbitMQProducer:
    __connection: pika.BlockingConnection
    __channel: pika.adapters.blocking_connection.BlockingChannel

    def __init__(self, server, port, username, password):
        params = pika.ConnectionParameters(server, credentials=pika.PlainCredentials(username, password), port=port)
        self.__connection = pika.BlockingConnection(params)
        self.__channel = self.__connection.channel()

    def publish(self, exchange, topic, data):
        self.__channel.basic_publish(exchange=exchange, routing_key=topic, body=data)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__connection.close()

    def __del__(self):
        self.__connection.close()


class RabbitMQSyncConsumer:
    __exchange: str
    __queue: str
    __connection: pika.BlockingConnection
    __channel: pika.adapters.blocking_connection.BlockingChannel

    def __init__(self, server, port, exchange, queue, username, password):
        params = pika.ConnectionParameters(server, credentials=pika.PlainCredentials(username, password), port=port)
        self.__connection = pika.BlockingConnection(params)
        self.__channel = self.__connection.channel()
        self.__exchange = exchange
        self.__queue = queue

    def consume(self, callback):
        self.__channel.basic_consume(queue=self.__queue, on_message_callback=callback, auto_ack=True)
        self.__channel.start_consuming()

    def stop_consuming(self):
        self.__channel.stop_consuming()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__connection.close()

    def __del__(self):
        self.__connection.close()


class RabbitMQAsyncConsumer:
    __exchange: str
    __queue: str
    __connection: pika.BlockingConnection
    __channel: pika.adapters.blocking_connection.BlockingChannel

    def __init__(self, server, port, exchange, queue, username, password):
        params = pika.ConnectionParameters(server, credentials=pika.PlainCredentials(username, password), port=port)
        self.__connection = pika.BlockingConnection(params)
        self.__channel = self.__connection.channel()
        self.__exchange = exchange
        self.__queue = queue

    def consume(self, callback):
        self.__channel.basic_consume(
            queue=self.__queue,
            on_message_callback=callback,
            auto_ack=True)

        def start_self():
            self.__channel.start_consuming()

        consumer_thread = threading.Thread(target=start_self)
        consumer_thread.start()

    def stop_consuming(self):
        self.__channel.stop_consuming()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__connection.close()

    def __del__(self):
        self.__connection.close()
