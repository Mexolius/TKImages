from abc import ABCMeta, abstractmethod
from typing import Callable, Union

Comparable = Union[float, int]


def get_comparator(comparator: str, threshold=0) -> Callable[[Comparable, Comparable], bool]:
    return {"==": lambda checked, reference: abs(checked - reference) < threshold,
            ">": lambda checked, reference: checked > reference,
            ">=": lambda checked, reference: checked >= reference,
            "<": lambda checked, reference: checked < reference,
            "<=": lambda checked, reference: checked <= reference}[comparator]
