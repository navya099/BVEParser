from OpenBveApi.Math.Vectors.Vector2 import Vector2
from Plugins.RouteCsvRw.Structures.AbstractStructure import AbstractStructure


class DestinationEvent(AbstractStructure):
    def __init__(self, track_position: float, event_type: int, trigger_once: bool, beacon_structure_index: int,
                 next_destination: int, previous_destination: int, position: Vector2,
                 yaw: float, pitch: float, roll: float,):
        super().__init__(track_position)
        self.event_type = event_type
        self.trigger_once = trigger_once
        self.beacon_structure_index = beacon_structure_index
        self.next_destination = next_destination
        self.previous_destination = previous_destination
        self.position = position
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll
