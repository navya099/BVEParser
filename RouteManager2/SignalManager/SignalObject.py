from abc import ABC

from OpenBveApi.Math.Vectors.Vector3 import Vector3
from OpenBveApi.World.Transformations import Transformation


class SignalObject(ABC):
    """An abstract signal object - All signals must inherit from this class"""
    def create(self, wpos: Vector3, rail_transformation: Transformation, local_transformation: Transformation,
               section_index: int, starting_distance: float, ending_distance, track_position: float, brightness: float):
        pass
