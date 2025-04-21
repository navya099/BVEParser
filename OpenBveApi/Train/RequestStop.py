from dataclasses import dataclass


@dataclass
class RequestStop:
    station_index: int
    max_cars: int
    probability: int
    time: -1
    stop_message: str
    pass_message: str
    full_speed: bool

