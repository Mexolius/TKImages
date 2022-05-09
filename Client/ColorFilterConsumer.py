import logging
import traceback

from ColorFilter.ColorFilter import process_request
from Logger.CustomLogFormatter import CustomLogFormatter
from RabbitMq.Query import ResultResponse
from RabbitMq.RabbitMQClient import RabbitMQSyncConsumer, RabbitMQProducer, RabbitMQAsyncConsumer
from Utils.Utils import setup_health_consumer

logger = logging.getLogger("ColorFilterConsumer")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomLogFormatter())
logger.addHandler(ch)

SERVICE_NAME = 'color_service'


if __name__ == '__main__':
    logger.info("Starting ColorFilterConsumer")
    consumer = RabbitMQSyncConsumer.from_config('colors')
    producer = RabbitMQProducer.from_config()
    health_consumer = RabbitMQAsyncConsumer.from_config('health')
    logger.info("ColorFilterConsumer started successfully")

    logger.info("Starting HealthConsumer")
    setup_health_consumer(SERVICE_NAME, producer, health_consumer)
    logger.info("HealthConsumer started successfully")


    def callback(ch, method, properties, body):
        logger.info(" [x] Received %r" % body)
        try:
            result = process_request(body)
            producer.publish_rmq_message(result)
        except Exception as e:
            logging.error(traceback.format_exc())
            resp = ResultResponse(500, [], SERVICE_NAME)
            producer.publish_rmq_message(resp)

    consumer.consume(callback)
