
import math
import numpy as np
from OpenBveApi.Math.Vectors.Vector3 import Vector3

class Transformation:
    def __init__(self, *args):
        if len(args) == 0:

            self.X = Vector3.Right()
            self.Y = Vector3.Down()
            self.Z = Vector3.Forward()
        elif len(args) == 3 and all(isinstance(a, (int, float)) for a in args):
            yaw, pitch, roll = args
            if yaw == 0.0 and pitch == 0.0 and roll == 0.0:
                self.X = Vector3.Right()
                self.Y = Vector3.Down()
                self.Z = Vector3.Forward()
            elif pitch == 0.0 and roll == 0.0:

                cos_yaw = math.cos(yaw)
                sin_yaw = math.sin(yaw)
                self.X = Vector3(cos_yaw, 0.0, -sin_yaw)
                self.Y = Vector3.Down()
                self.Z = Vector3(sin_yaw, 0.0, cos_yaw)
            else:
                self.X = Vector3.Right()
                self.Y = Vector3.Down()
                self.Z = Vector3.Forward()
                self.X.rotate(self.Y, yaw)
                self.Z.rotate(self.Y, yaw)
                self.Y.rotate(self.X, -pitch)
                self.Z.rotate(self.X, -pitch)
                self.X.rotate(self.Z, -roll)
                self.Y.rotate(self.Z, -roll)
        elif len(args) == 4 and isinstance(args[0], Transformation):
            base, yaw, pitch, roll = args
            self.X = base.X.clone()  # base.X에서 clone()을 호출
            self.Y = base.Y.clone()  # base.Y에서 clone()을 호출
            self.Z = base.Z.clone()  # base.Z에서 clone()을 호출
            self.X.rotate(self.Y, yaw)
            self.Z.rotate(self.Y, yaw)

            # In the left-handed coordinate system, the clock-wise rotation is positive when the origin is
            # viewed from the positive direction of the axis.
            self.Y.rotate(self.X, -pitch)
            self.Z.rotate(self.X, -pitch)
            self.X.rotate(self.Z, -roll)
            self.Y.rotate(self.Z, -roll)
        elif len(args) == 2 and all(isinstance(a, Transformation) for a in args):
            t1, t2 = args
            self.X = t1.X.copy()
            self.Y = t1.Y.copy()
            self.Z = t1.Z.copy()
            self.X.rotate(t2)
            self.Y.rotate(t2)
            self.Z.rotate(t2)
        elif len(args) == 3 and all(isinstance(a, Vector3) for a in args):
            self.Z, self.Y, self.X = args
        else:
            raise ValueError("Invalid constructor arguments for Transformation.")

    def to_matrix4d(self):
        # Row-major 4x4 matrix with right-handed coordinate system

        return np.array([
            [self.X.X, self.X.Y, -self.X.Z, 0.0],
            [self.Y.X, self.Y.Y, -self.Y.Z, 0.0],
            [-self.Z.X, -self.Z.Y, self.Z.Z, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])


# NullTransformation static equivalent
NullTransformation = Transformation()
