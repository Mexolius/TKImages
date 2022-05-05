TOLERANCE = 15


def color_percentage(expected, actual):
    if hasattr(actual, '__iter__'):
        return all([abs(x - y) < TOLERANCE for x, y in zip(expected, actual)])
    else:
        return abs(sum(expected)/len(expected) - actual) < TOLERANCE
