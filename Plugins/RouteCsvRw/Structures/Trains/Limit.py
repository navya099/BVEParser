from OpenBveApi.Math.Vectors.Vector2 import Vector2
from Plugins.RouteCsvRw.Structures.AbstractStructure import AbstractStructure


class Limit(AbstractStructure):
    """
    Attributes:
        speed: The speed limit to be enforced. Stored in km/h, has been transformed by UnitOfSpeed if appropriate
        direction: The side of the auto-generated speed limit post
        cource: The cource (little arrow) on the speed limit post denoting a diverging JA limit
    """
    def __init__(self, track_position: float, speed: float, direction: int, cource: int, rail_index: int):
        super().__init__(track_position, rail_index)
        self.speed = speed
        self.direction = direction
        self.cource = cource