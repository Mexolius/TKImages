import os
import json
import imagesize
from Utils.Utils import get_comparator

INCH2CM = 0.393701

def check_size_in_KB(path):
    size_in_b = os.path.getsize(path)
    size_in_KB = size_in_b / 1024
    return size_in_KB


def pixels_to_cm(pixels, DPI):
    return pixels/DPI*INCH2CM


def check_size_in_cm(path):
    width, height = imagesize.get(path)
    widthDPI, heightDPI = imagesize.getDPI(path)
    return [pixels_to_cm(width,widthDPI), pixels_to_cm(height,heightDPI)]

def get_comparator(comparator, threshold=0):
    return {"==": lambda reference, checked: abs(reference - checked) <= threshold,
            ">": lambda reference, checked: reference > checked,
            ">=": lambda reference, checked: reference >= checked,
            "<": lambda reference, checked: reference < checked,
            "<=": lambda reference, checked: reference <= checked}[comparator]


def filter_by_KB(paths, reference, comparator, threshold):
    filtered_paths = []
    comparator = get_comparator(comparator, threshold)
    for path in paths:
        if comparator(check_size_in_KB(path), reference):
            filtered_paths.append(path)
    return filtered_paths


def filter_by_pixels(paths, reference, comparator, threshold):
    filtered_paths = []
    comparator = get_comparator(comparator, threshold)
    for path in paths:
        width, height = imagesize.get(path)
        if comparator(reference[0], width) and comparator(reference[1], height):
            filtered_paths.append(path)
    return filtered_paths


def filter_by_cm(paths, reference, comparator, threshold):
    filtered_paths = []
    comparator = get_comparator(comparator, threshold)
    for path in paths:
        size_in_cm = check_size_in_cm(path) 
        if comparator(reference[0], size_in_cm[0]) and comparator(reference[1], size_in_cm[1]):
            filtered_paths.append(path)
    return filtered_paths


def get_filter_and_refernce(params):
    return {"kb": (filter_by_KB, float(params["kb"]) if 'kb' in params else 0),
            "pixels": (filter_by_pixels, params["pixels"] if 'pixels' in params else 0),
            "cm": (filter_by_cm, params["cm"] if 'cm' in params else 0)
            }[params["unit"]]


def process_request(body: str):
    body = json.loads(body)
    params = body["params"]
    threshold =  float(params['threshold']) if 'threshold' in params else 0
    filter_method, reference = get_filter_and_refernce(params) 

    result = filter_method(paths=body["paths"], reference=reference, comparator=params["comparator"],threshold=threshold)
    return result