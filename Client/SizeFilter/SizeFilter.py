import os

import imagesize
from Utils.Utils import get_comparator


def check_size_in_KB(path):
    size_in_b = os.path.getsize(path)
    size_in_KB = size_in_b / 1024
    return size_in_KB


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
