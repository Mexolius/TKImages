def eight_bit_to_rgb(pixel):
    r = (pixel >> 5) * 255 / 7
    g = ((pixel >> 2) & 0x07) * 255 / 7
    b = (pixel & 0x03) * 255 / 3
    return r, g, b


def color_percentage(data_record, expected, tolerance):
    if hasattr(data_record, '__iter__'):
        return lambda pixel: all([abs(x - y) < tolerance for x, y in zip(expected, pixel)])
    else:
        return lambda pixel: all([abs(x - y) < tolerance for x, y in zip(expected, eight_bit_to_rgb(pixel))])
