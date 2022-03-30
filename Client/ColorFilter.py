import json

from Query import ResultResponse
from Color import ColorParams, ColorMetric, Color
from PIL import ImageStat, Image
from typing import Callable

SERVICE_NAME = "color service"


def get_comparator(comparator, threshold=0) -> Callable[[Color, Color], bool]:
    return {"==": lambda checked, reference: any(abs(r - c) < threshold for r, c in zip(checked, reference)),
            "<": lambda checked, reference: any(r < c for r, c in zip(checked, reference)),
            "<=": lambda checked, reference: any(r <= c for r, c in zip(checked, reference)),
            ">": lambda checked, reference: any(r > c for r, c in zip(checked, reference)),
            ">=": lambda checked, reference: any(r >= c for r, c in zip(checked, reference))
            }[comparator]


def get_processing_metric(metric: ColorMetric):
    return {
        "max": lambda stat: stat.extrema[:, 1],
        "min": lambda stat: stat.extrema[:, 0],
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
        return comparator(
            metric(ImageStat.Stat(Image.open(path))),
            params.color
        )

    result = filter(is_compliant, paths)
    return ResultResponse(200, result, SERVICE_NAME)
