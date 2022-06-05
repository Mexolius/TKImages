from WeatherFilter.lib.classifier import classifier
import json
import os


def run_classifier(path):

    image_classification = classifier(path)
    return image_classification


def check_weather(paths, weather_type, precision):
    filtered_paths = []
    for path in paths:
        classification = run_classifier(path)
        top_n_weather_types = list(classification.keys())[:precision+1]
        if weather_type in top_n_weather_types:
            filtered_paths.append(path)
    return filtered_paths


def process_request(body):
    body = json.loads(body)
    params = body["params"]

    result = check_weather(paths=body["paths"],
                           weather_type=params["type"], precision=params["precision"])
    return result
