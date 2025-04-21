from dataclasses import dataclass


@dataclass
class Station:
    name: str
    arrival_time: float
    departure_time: float
