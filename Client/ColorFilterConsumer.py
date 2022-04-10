from Logger.CustomLogFormatter import CustomLogFormatter
from ColorFilter.ColorFilter import process_request
from RabbitMq.RabbitMQClient import RabbitMQSyncConsumer, RabbitMQProducer
from RabbitMq.Query import ResultResponse

import traceback
import logging

logger = logging.getLogger("ColorFilterConsumer")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomLogFormatter())
logger.addHandler(ch)


if __name__ == '__main__':
    logger.info("Starting ColorFilterConsumer")
    consumer = RabbitMQSyncConsumer.from_config('colors')
    producer = RabbitMQProducer.from_config()
    logger.info("ColorFilterConsumer started successfully")


    def callback(ch, method, properties, body):
        try:
            result = process_request(body)
            producer.publish_rmq_message(result)
        except Exception as e:
            logging.error(traceback.format_exc())
            resp = ResultResponse(500, [], 'color_service')
            producer.publish_rmq_message(resp)

    consumer.consume(callback)
