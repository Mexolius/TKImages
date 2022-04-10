import sys
import json
import logging
import traceback
import sys

from Logger.CustomLogFormatter import CustomLogFormatter
from RabbitMq.Query import ResultResponse
from RabbitMq.RabbitMQClient import RabbitMQProducer, RabbitMQSyncConsumer
from SizeFilter.SizeFilter import process_request

logger = logging.getLogger("SizeFilterConsumer")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomLogFormatter())
logger.addHandler(ch)

SERVICE_NAME = "size_service"


def send_result(prod, result):
    prod.publish(result.exchange(), result.topic(), result.json())


if __name__ == '__main__':
    logger.info("Starting SizeFilterConsumer")
    consumer = RabbitMQSyncConsumer('localhost', 5672, 'ImageFinder', 'image_finder.size', 'myuser', 'mypassword')
    producer = RabbitMQProducer('localhost', 5672, 'myuser', 'mypassword')
    logger.info("SizeFilterConsumer started successfully")


    def callback(ch, method, properties, body):
        logger.info(" [x] Received %r" % body)
        try:
            result = process_request(body)
            resp = ResultResponse(200, result, SERVICE_NAME)
        except Exception as e:
            logging.error(traceback.format_exc())
            resp = ResultResponse(500, [], SERVICE_NAME)          
        producer.publish(resp.exchange(), resp.topic(), resp.json())

    consumer.consume(callback)
