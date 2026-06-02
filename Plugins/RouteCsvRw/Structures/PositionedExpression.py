from dataclasses import dataclass, field

from .Expression import Expression


@dataclass
class PositionedExpression:
    track_position: float
    expression: Expression = field(default=None)