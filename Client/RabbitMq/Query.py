import json
import logging

from typing import Sequence
from abc import ABC, abstractmethod
from Logger.CustomLogFormatter import CustomLogFormatter

logger = logging.getLogger("Query")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomLogFormatter())
logger.addHandler(ch)


class RabbitMQMessage(ABC):
    @staticmethod
    def exchange():
        return 'ImageFinder'

    @staticmethod
    @abstractmethod
    def topic():
        pass

    def json(self):
        return json.dumps(self.__dict__)


class Query(RabbitMQMessage, ABC):
    def __init__(self, paths: Sequence[str], params):
        params = {k: v for k, v in params.items() if v is not None and v != ""}
        self.path_number = len(paths)
        self.paths = paths
        self.param_number = len(params)
        self.params = params


class ResultResponse(RabbitMQMessage):
    def __init__(self, result, paths, sender):
        self.result = result
        self.paths = paths
        self.total = len(paths)
        self.sender = sender

    @staticmethod
    def topic():
        return 'results'


class HealthRequestMessage(RabbitMQMessage):
    def __init__(self, service_name):
        self.service_name = service_name

    @staticmethod
    def topic():
        return 'health'


class HealthResponseMessage(RabbitMQMessage):
    def __init__(self, service_name):
        self.service_name = service_name

    @staticmethod
    def topic():
        return 'health_response'


class SizeQuery(Query):
    def __init__(self, paths, params):
        super().__init__(paths, params)

    @staticmethod
    def topic():
        return 'size'


class DogsQuery(Query):
    def __init__(self, paths, params):
        super().__init__(paths, params)

    @staticmethod
    def topic():
        return 'dogs_breeds'


class SimilarityQuery(Query):
    def __init__(self, paths, params):
        super().__init__(paths, params)

    @staticmethod
    def topic():
        return 'similarity'

class FacesQuery(Query):
    def __init__(self, paths, params):
        super().__init__(paths, params)

    @staticmethod
    def topic():
        return 'faces_smiles'


class SimpleQuery(Query):
    def __init__(self, paths: Sequence[str], data, moreData):
        params = {"data": data, "moreData": moreData}
        super().__init__(paths, params)

    @staticmethod
    def topic():
        return 'size'
