from Logger.CustomLogFormatter import CustomLogFormatter
from ColorFilter.ColorFilter import process_request
from RabbitMq.RabbitMQClient import RabbitMQSyncConsumer, RabbitMQProducer
from RabbitMq.Query import ResultResponse

import traceback
import logging

logger = logging.getLogger("SimpleFilterConsumer")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomLogFormatter())
logger.addHandler(ch)


if __name__ == '__main__':
    logger.info("Starting ColorFilterConsumer")
    consumer = RabbitMQSyncConsumer('localhost', 5672, 'ImageFinder', 'image_finder.colors', 'myuser', 'mypassword')
    producer = RabbitMQProducer('localhost', 5672, 'myuser', 'mypassword')
    logger.info("ColorFilterConsumer started successfully")


    def callback(ch, method, properties, body):
        try:
            result = process_request(body)
            producer.publish(result.exchange(), result.topic(), result.json())
        except Exception as e:
            logging.error(traceback.format_exc())
            resp = ResultResponse(500, [], 'color_service')
            producer.publish(resp.exchange(), resp.topic(), resp.json())

    consumer.consume(callback)
