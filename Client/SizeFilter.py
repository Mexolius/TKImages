import os

def check_size_in_KB(path):
    size_in_b = os.path.getsize(path)
    size_in_KB = size_in_b/1024
    return size_in_KB

def compare(reference , checked, comparator, threshold = 0):
    if comparator == "==":
        return abs(reference - checked) < threshold
    elif comparator == ">":
        return checked > reference
    elif comparator == ">=":
        return checked >= reference
    elif comparator == "<":
        return checked < reference
    elif comparator == "<=":
        return checked <= reference
    else:
        raise ValueError


def filter_by_KB(paths, reference, comparator, threshold):
    filtered_paths = []
    for path in paths:
        if compare(reference, check_size_in_KB(path), comparator, threshold):
            filtered_paths.append(path)
    return filtered_paths

