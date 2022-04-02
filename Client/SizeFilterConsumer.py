import json
import logging

from Logger.CustomLogFormatter import CustomLogFormatter
from RabbitMq.Query import ResultResponse
from RabbitMq.RabbitMQClient import RabbitMQSyncConsumer, RabbitMQProducer
from SizeFilter.SizeFilter import filter_by_KB

logger = logging.getLogger("SimpleFilterConsumer")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomLogFormatter())
logger.addHandler(ch)

SENDER = "Size"


def send_result(prod, result):
    prod.publish(result.exchange(), result.topic(), result.json())


if __name__ == '__main__':
    logger.info("Starting SizeFilterConsumer")
    consumer = RabbitMQSyncConsumer('localhost', 5672, 'ImageFinder', 'image_finder.size', 'myuser', 'mypassword')
    producer = RabbitMQProducer('localhost', 5672, 'myuser', 'mypassword')
    logger.info("SizeFilterConsumer started successfully")


    def callback(ch, method, properties, body):
        logger.info(" [x] Received %r" % body)
        body = json.loads(body)
        logger.info(body)
        params = body["params"]
        if params["unit"] == "kb":
            if "threshold" in params.keys():
                threshold = float(params["threshold"])
            else:
                threshold = 0

            res = filter_by_KB(paths=body["paths"], reference=float(params["kb"]), comparator=params["comparator"],
                               threshold=threshold)
            result = ResultResponse(200, res, SENDER)
        else:
            result = ResultResponse(501, [], SENDER)
        send_result(producer, result)


    consumer.consume(callback)
