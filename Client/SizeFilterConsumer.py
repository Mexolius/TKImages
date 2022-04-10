import sys
import json
import logging
import sys

from Logger.CustomLogFormatter import CustomLogFormatter
from RabbitMq.Query import ResultResponse
from RabbitMq.RabbitMQClient import RabbitMQProducer, RabbitMQSyncConsumer
from SizeFilter.SizeFilter import filter_by_KB, filter_by_pixels

logger = logging.getLogger("SizeFilterConsumer")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomLogFormatter())
logger.addHandler(ch)

SENDER = "Size"

if __name__ == '__main__':
    logger.info("Starting SizeFilterConsumer")
    consumer = RabbitMQSyncConsumer.from_config('size')
    producer = RabbitMQProducer.from_config()
    logger.info("SizeFilterConsumer started successfully")


    def callback(ch, method, properties, body):
        logger.info(" [x] Received %r" % body)
        body = json.loads(body)
        logger.info(body)
        params = body["params"]

        if "threshold" in params.keys():
            threshold = float(params["threshold"])
        else:
            threshold = 0
        try:
            if params["unit"] == "kb":
                res = filter_by_KB(paths=body["paths"], reference=float(params["kb"]), comparator=params["comparator"],
                                   threshold=threshold)
                result = ResultResponse(200, res, SENDER)
            elif params["unit"] == "pixels":
                res = filter_by_pixels(paths=body["paths"], reference=params["pixels"], comparator=params["comparator"],
                                       threshold=threshold)
                result = ResultResponse(200, res, SENDER)
            else:
                result = ResultResponse(501, [], SENDER)
        except Exception as e:
            result = ResultResponse(404, [], SENDER)
            logger.info(f"Exception {e}")
            logger.info(sys.exc_info()[0])

        producer.publish_rmq_message(result)

    consumer.consume(callback)
