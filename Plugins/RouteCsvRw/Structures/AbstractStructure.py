from abc import ABC


class AbstractStructure(ABC):
    def __init__(self, track_position: float, rail_index: int = 0):
        self.TrackPosition = track_position
        self.RailIndex = rail_index
