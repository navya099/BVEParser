from dataclasses import dataclass


@dataclass
class Pole:
    Exists: bool = False
    Mode: int = 0
    Location: float = 0.0
    Interval: float = 0.0
    Type: int = 0

