import json

from Query import ResultResponse
from RabbitMQClient import RabbitMQSyncConsumer, RabbitMQProducer
from SizeFilter import filter_by_KB, filter_by_pixels

SENDER = "Size"


def send_result(prod, result):
    prod.publish(result.exchange(), result.topic(), result.json())


if __name__ == '__main__':
    consumer = RabbitMQSyncConsumer('localhost', 5672, 'ImageFinder', 'image_finder.size', 'myuser', 'mypassword')
    producer = RabbitMQProducer('localhost', 5672, 'myuser', 'mypassword')


    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)
        body = json.loads(body)
        print(body)
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
            # logger.info(f"Exception {e}")
            # logger.info(sys.exc_info()[0])

        send_result(producer, result)


    consumer.consume(callback)
