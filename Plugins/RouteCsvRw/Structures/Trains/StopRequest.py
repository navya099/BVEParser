from dataclasses import dataclass


@dataclass
class StopRequest:
    station_index: int
    max_number_of_cars: int
    track_position: float
