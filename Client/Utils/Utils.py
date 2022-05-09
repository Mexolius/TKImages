import json
from typing import Callable, Union

from RabbitMq.Query import HealthResponseMessage

Comparable = Union[float, int]


def get_comparator(comparator: str, threshold=0) -> Callable[[Comparable, Comparable], bool]:
    return {"==": lambda checked, reference: abs(checked - reference) < threshold,
            ">": lambda checked, reference: checked > reference,
            ">=": lambda checked, reference: checked >= reference,
            "<": lambda checked, reference: checked < reference,
            "<=": lambda checked, reference: checked <= reference}[comparator]


def setup_health_consumer(service_name, producer, health_consumer):
    health_message = HealthResponseMessage(service_name)

    def health_callback(ch, method, properties, body):
        if json.loads(body)['service_name'] == service_name:
            producer.publish_rmq_message(health_message)
            health_consumer.ack(method.delivery_tag)

    health_consumer.consume(health_callback)
