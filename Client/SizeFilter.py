import os
from Utils import get_comparator


def check_size_in_KB(path):
    size_in_b = os.path.getsize(path)
    size_in_KB = size_in_b / 1024
    return size_in_KB


def filter_by_KB(paths, reference, comparator, threshold):
    filtered_paths = []
    comparator = get_comparator(comparator, threshold)
    for path in paths:
        if comparator(check_size_in_KB(path), reference):
            filtered_paths.append(path)
    return filtered_paths
