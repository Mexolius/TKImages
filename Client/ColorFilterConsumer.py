from ColorFilter import process_request
from RabbitMQClient import RabbitMQSyncConsumer, RabbitMQProducer
from Query import ResultResponse

import traceback
import logging

if __name__ == '__main__':
    consumer = RabbitMQSyncConsumer('localhost', 5672, 'ImageFinder', 'image_finder.colors', 'myuser', 'mypassword')
    producer = RabbitMQProducer('localhost', 5672, 'myuser', 'mypassword')


    def callback(ch, method, properties, body):
        try:
            result = process_request(body)
            producer.publish(result.exchange(), result.topic(), result.json())
        except Exception as e:
            logging.error(traceback.format_exc())
            resp = ResultResponse(500, [], 'color_service')
            producer.publish(resp.exchange(), resp.topic(), resp.json())

    consumer.consume(callback)
