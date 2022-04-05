import json

from Query import ResultResponse
from Color import ColorParams, ColorMetric
from PIL import ImageStat, Image
from Utils import get_comparator

SERVICE_NAME = "color service"


def get_processing_metric(metric: ColorMetric):
    return {
        "max": lambda stat: map(lambda x: x[1], stat.extrema),
        "min": lambda stat: map(lambda x: x[0], stat.extrema),
        "mean": lambda stat: stat.mean,
        "median": lambda stat: stat.median,
        "rms": lambda stat: stat.rms
    }[metric.name]


def process_request(body: str) -> ResultResponse:
    request = json.loads(body)
    paths = request['paths']
    raw_params = request['params']
    params = ColorParams.from_object(raw_params)

    metric = get_processing_metric(params.metric)
    comparator = get_comparator(params.comparator, params.threshold)

    def is_compliant(path):
        return all(map(
            comparator,
            metric(ImageStat.Stat(Image.open(path))),
            params.color
        ))

    result = list(filter(is_compliant, paths))
    return ResultResponse(200, result, SERVICE_NAME)
