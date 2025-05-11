from OpenBveApi.Math.Vectors.Vector3 import Vector3
from OpenBveApi.World.Transformations import Transformation
from Plugins.RouteCsvRw.ObjectDictionary import ObjectDictionary
from Plugins.RouteCsvRw.Structures.AbstractStructure import AbstractStructure
from OpenBveApi.Math.Vectors.Vector2 import Vector2


class FreeObj(AbstractStructure):
    def __init__(self, track_position: float, objtype: int, position: Vector2,
                 yaw: float, pitch: float = 0, roll: float = 0):
        super().__init__(track_position)
        self.Position = position
        self.Type: int = objtype
        self.Yaw: float = yaw
        self.Pitch: float = pitch
        self.Roll: float = roll

    def CreateRailAligned(self, FreeObjects: ObjectDictionary, WorldPosition: Vector3,
                          RailTransformation: Transformation, StartingDistance: float, EndingDistance: float) -> tuple[Vector3, str]:
        dz = self.TrackPosition - StartingDistance
        WorldPosition += self.Position.x * RailTransformation.X + \
                         self.Position.y * RailTransformation.Y + \
                         dz * RailTransformation.Z
        obj = FreeObjects.get(self.Type)
        '''
        if obj is not None:
            obj.CreateObject(
                WorldPosition,
                RailTransformation,
                Transformation(
                    self.Yaw,
                    self.Pitch,
                    self.Roll
                ),
                StartingDistance,
                EndingDistance,
                self.TrackPosition
            )
        '''
        return WorldPosition ,obj

    def CreateGroundAligned(self):
        pass
