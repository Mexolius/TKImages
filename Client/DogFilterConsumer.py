import logging
import traceback

from DogsFilter.DogsBreedFilter import process_request
from Logger.CustomLogFormatter import CustomLogFormatter
from RabbitMq.Query import ResultResponse
from RabbitMq.RabbitMQClient import RabbitMQProducer, RabbitMQSyncConsumer

logger = logging.getLogger("DogFilterConsumer")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomLogFormatter())
logger.addHandler(ch)

SERVICE_NAME = "dog_service"

if __name__ == '__main__':
    logger.info("Starting DogFilterConsumer")
    consumer = RabbitMQSyncConsumer.from_config('dogs_breeds')
    producer = RabbitMQProducer.from_config()
    logger.info("DogFilterConsumer started successfully")


    def callback(ch, method, properties, body):
        logger.info(" [x] Received %r" % body)
        try:
            result = process_request(body)
            resp = ResultResponse(200, result, SERVICE_NAME)
        except Exception as e:
            logging.error(traceback.format_exc())
            resp = ResultResponse(500, [], SERVICE_NAME)
        producer.publish_rmq_message(resp)
        logger.info("DogFilterConsumer Finished Processing")


    consumer.consume(callback)
