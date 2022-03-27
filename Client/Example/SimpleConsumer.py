from RabbitMQClient import RabbitMQSyncConsumer, RabbitMQProducer
from Query import ResultResponse


def send_result(prod, result):
    prod.publish(result.exchange(), result.queue(), result.json())


if __name__ == '__main__':
    consumer = RabbitMQSyncConsumer('localhost', 5672, 'ImageFinder', 'image_finder.size', 'myuser', 'mypassword')
    producer = RabbitMQProducer('localhost', 5672, 'myuser', 'mypassword')

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)

        consumer.stop_consuming()
        result = ResultResponse(404, ["path1", "path2"], "THE SENDER")
        send_result(producer, result)


    consumer.consume(callback)
