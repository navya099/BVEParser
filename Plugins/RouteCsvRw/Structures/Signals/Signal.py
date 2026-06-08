from OpenBveApi.Math.Vectors.Vector2 import Vector2
from Plugins.RouteCsvRw.Structures.AbstractStructure import AbstractStructure
from RouteManager2.SignalManager.SignalObject import SignalObject


class Signal(AbstractStructure):
    def __init__(self, track_position: float, section_index: int, signal_object: SignalObject,
                 position: Vector2, yaw: float, pitch: float, roll: float, show_object: bool, show_post: bool):
        super().__init__(track_position)
        self.section_index = section_index
        self.signal_object = signal_object
        self.position = position
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll
        self.show_object = show_object
        self.show_post = show_post
