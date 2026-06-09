from OpenBveApi.Math.Vectors.Vector2 import Vector2
from Plugins.RouteCsvRw.Structures.AbstractStructure import AbstractStructure


class Transponder(AbstractStructure):
    def __init__(self, track_position: float, event_type: int, data: int,
                 position: Vector2, section_index: int, beacon_structure_index: int = -1,
                 clip_to_first_red_section: bool = True,
                 yaw: float = 0.0, pitch: float= 0.0, roll: float = 0.0):
        super().__init__(track_position)
        self.event_type = event_type
        self.data = data
        self.beacon_structure_index = beacon_structure_index
        self.position = position
        self.section_index = section_index
        self.clip_to_first_red_section = clip_to_first_red_section
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll
