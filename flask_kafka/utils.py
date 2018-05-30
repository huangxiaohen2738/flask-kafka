import itertools


def slicer(data_list, parts):
    result = []
    for __ in range(parts):
        result.append([])
    for value, container in zip(data_list, itertools.cycle(result)):
        container.append(value)
    return result
