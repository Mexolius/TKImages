from Query import SimpleQuery, QueryExecutor
from RabbitMQClient import RabbitMQProducer, RabbitMQAsyncConsumer

if __name__ == '__main__':
    consumer = RabbitMQAsyncConsumer('localhost', 5672, 'ImageFinder', 'image_finder.results', 'myuser', 'mypassword')


    def callback(ch, method, properties, body):
        consumer.stop_consuming()
        print(" [x] Received %r" % body)


    producer = RabbitMQProducer('localhost', 5672, 'myuser', 'mypassword')
    executor = QueryExecutor(producer)

    query = SimpleQuery(["path1", "path2"], "Hello", "Hi")
    executor.execute([query])

    consumer.consume(callback)
