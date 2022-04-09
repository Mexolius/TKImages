import json

from RabbitMq.Query import ResultResponse
from . import Color
from PIL import ImageStat, Image
from Utils.Utils import get_comparator

SERVICE_NAME = "color service"


def get_processing_metric(metric: Color.ColorMetric):
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
    params = Color.ColorParams.from_object(raw_params)

    metric = get_processing_metric(params.metric)
    comparator = get_comparator(params.comparator, params.threshold)

    def is_compliant(path):
        calc_metric = metric(ImageStat.Stat(Image.open(path)))
        if len(calc_metric) > 2:
            return all(map(
                comparator,
                calc_metric,
                params.color
            ))
        elif len(calc_metric) == 1:
            colors = (params.color[0] + params.color[1] + params.color[2])/3
            return comparator(calc_metric[0], colors)
        else:  # This is not a normal image. I refuse to return it.
            return False

    result = list(filter(is_compliant, paths))
    return ResultResponse(200, result, SERVICE_NAME)
