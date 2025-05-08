from dataclasses import dataclass
from typing import ClassVar

from OpenBveApi.Math.Vectors.Vector3 import Vector3


@dataclass
class Orientation3:
    X: Vector3
    Y: Vector3
    Z: Vector3

    # Static readonly fields
    Null: ClassVar['Orientation3']
    Default: ClassVar['Orientation3']

    def __eq__(self, other):
        if not isinstance(other, Orientation3):
            return NotImplemented
        return self.X == other.X and self.Y == other.Y and self.Z == other.Z

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.X, self.Y, self.Z))


# Define after class to handle circular reference to Vector3
Orientation3.Null = Orientation3(Vector3.Zero(), Vector3.Zero(), Vector3.Zero())
Orientation3.Default = Orientation3(Vector3.Right(), Vector3.Up(), Vector3.Forward())
