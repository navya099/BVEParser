from Plugins.RouteCsvRw.RouteData import RouteData
from .Structures.Expression import Expression
from typing import List


class PreprocessMixin2:
    def __init__(self):
        pass

    def pre_proces_options(self, expressions: List[Expression], data: RouteData, unit_of_length: List[float], previewonly: bool) -> None:
        section = ''
        section_always_prefix = False
        # process expressions
        for j in range(len(expressions)):
            if self.IsRW and expressions[j].Text.StartsWith("[") and expressions[j].Text.EndsWith("]"):
                pass

