import logging
import traceback

from Similarity.SimilarityFilter import process_request
from Logger.CustomLogFormatter import CustomLogFormatter
from RabbitMq.Query import ResultResponse
from RabbitMq.RabbitMQClient import RabbitMQProducer, RabbitMQSyncConsumer

logger = logging.getLogger("SimilarityConsumer")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomLogFormatter())
logger.addHandler(ch)

SERVICE_NAME = "similarity_service"

if __name__ == '__main__':
    logger.info("Starting SimilarityConsumer")
    consumer = RabbitMQSyncConsumer.from_config('similarity')
    producer = RabbitMQProducer.from_config()
    logger.info("SimilarityConsumer started successfully")


    def callback(ch, method, properties, body):
        logger.info(" [x] Received %r" % body)

        result = process_request(body, logger)
        print(result)
        resp = ResultResponse(200, result, SERVICE_NAME)

        producer.publish_rmq_message(resp)
        logger.info("SimilarityConsumer Finished Processing")


    consumer.consume(callback)
