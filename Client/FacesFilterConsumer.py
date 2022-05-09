import sys
import json
import logging
import traceback
import sys

from Logger.CustomLogFormatter import CustomLogFormatter
from RabbitMq.Query import ResultResponse
from RabbitMq.RabbitMQClient import RabbitMQProducer, RabbitMQSyncConsumer
from FacesFilter.FacesFilter import process_request

logger = logging.getLogger("FacesFilterConsumer")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomLogFormatter())
logger.addHandler(ch)

SERVICE_NAME = "faces_service"

if __name__ == '__main__':
    logger.info("Starting FacesFilterConsumer")
    consumer = RabbitMQSyncConsumer.from_config('faces_smiles')
    producer = RabbitMQProducer.from_config()
    logger.info("FacesFilterConsumer started successfully")


    def callback(ch, method, properties, body):
        logger.info(" [x] Received %r" % body)
        try:
            result = process_request(body)
            resp = ResultResponse(200, result, SERVICE_NAME)
        except Exception as e:
            logging.error(traceback.format_exc())
            resp = ResultResponse(500, [], SERVICE_NAME)  
        producer.publish_rmq_message(resp)
    
    consumer.consume(callback)
