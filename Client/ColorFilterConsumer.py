from ColorFilter import process_request
from RabbitMQClient import RabbitMQSyncConsumer, RabbitMQProducer

if __name__ == '__main__':
    consumer = RabbitMQSyncConsumer('localhost', 5672, 'ImageFinder', 'image_finder.color', 'myuser', 'mypassword')
    producer = RabbitMQProducer('localhost', 5672, 'myuser', 'mypassword')


    def callback(ch, method, properties, body):
        result = process_request(body)
        producer.publish(result.exchange(), result.topic(), result.json())

    consumer.consume(callback)
