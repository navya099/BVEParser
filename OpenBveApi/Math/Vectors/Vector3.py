from dataclasses import dataclass
import math
from typing import List, Tuple



@dataclass
class Vector3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    # ✅ 클래스 밖에서 초기화 (dataclass의 제한 피하기 위함)
    @classmethod
    def Forward(cls):
        return cls(0.0, 0.0, 1.0)

    @classmethod
    def Backward(cls):
        return cls(0.0, 0.0, -1.0)

    @classmethod
    def Zero(cls):
        return cls(0.0, 0.0, 0.0)

    @classmethod
    def Left(cls):
        return cls(-1.0, 0.0, 0.0)

    @classmethod
    def Right(cls):
        return cls(1.0, 0.0, 0.0)

    @classmethod
    def Down(cls):
        return cls(0.0, 1.0, 0.0)

    @classmethod
    def Up(cls):
        return cls(0.0, -1.0, 0.0)

    def clone(self):
        return Vector3(self.x, self.y, self.z)

    @staticmethod
    def get_vector3(vector2, y):
        norm = math.sqrt(vector2.x ** 2 + vector2.y ** 2 + y ** 2)
        if norm == 0.0:
            raise ZeroDivisionError("Cannot normalize a zero-length vector.")
        t = 1.0 / norm
        return Vector3(t * vector2.x, t * y, t * vector2.y)

    @staticmethod
    def cross(a, b):
        return Vector3(
            a.y * b.z - a.z * b.y,
            a.z * b.x - a.x * b.z,
            a.x * b.y - a.y * b.x
        )
    @classmethod
    def from_vector(cls, v: 'Vector3') -> 'Vector3':
        return cls(v.x, v.y, v.z)

    @classmethod
    def parse(cls, string_to_parse: str, separator: str = ',') -> 'Vector3':
        parts = string_to_parse.split(separator)
        try:
            x = float(parts[0]) if len(parts) > 0 else 0.0
            y = float(parts[1]) if len(parts) > 1 else 0.0
            z = float(parts[2]) if len(parts) > 2 else 0.0
        except ValueError:
            x = y = z = 0.0
        return cls(x, y, z)

    # 벡터 + 벡터
    def __add__(self, other):
        if isinstance(other, Vector3):
            return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
        elif isinstance(other, (int, float)):
            return Vector3(self.x + other, self.y + other, self.z + other)
        return NotImplemented

    def __iadd__(self, other):
        if isinstance(other, Vector3):
            self.x += other.x
            self.y += other.y
            self.z += other.z
            return self
        elif isinstance(other, (int, float)):
            self.x += other
            self.y += other
            self.z += other
            return self
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    # 벡터 - 벡터
    def __sub__(self, other):
        if isinstance(other, Vector3):
            return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
        elif isinstance(other, (int, float)):
            return Vector3(self.x - other, self.y - other, self.z - other)
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            return Vector3(other - self.x, other - self.y, other - self.z)
        return NotImplemented

    # 음수 벡터
    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)

    # 곱셈
    def __mul__(self, other):
        if isinstance(other, Vector3):
            return Vector3(self.x * other.x, self.y * other.y, self.z * other.z)
        elif isinstance(other, (int, float)):
            return Vector3(self.x * other, self.y * other, self.z * other)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    # 나눗셈
    def __truediv__(self, other):
        if isinstance(other, Vector3):
            if other.x == 0 or other.y == 0 or other.z == 0:
                raise ZeroDivisionError("Division by zero in Vector3")
            return Vector3(self.x / other.x, self.y / other.y, self.z / other.z)
        elif isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Division by zero scalar")
            factor = 1.0 / other
            return Vector3(self.x * factor, self.y * factor, self.z * factor)
        return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            if self.x == 0 or self.y == 0 or self.z == 0:
                raise ZeroDivisionError("Division by zero in Vector3")
            return Vector3(other / self.x, other / self.y, other / self.z)
        return NotImplemented

    # 비교
    def __eq__(self, other):
        if not isinstance(other, Vector3):
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def normalize(self):
        norm = self.x ** 2 + self.y ** 2 + self.z ** 2
        if norm == 0.0:
            return
        factor = 1.0 / math.sqrt(norm)
        self.x *= factor
        self.y *= factor
        self.z *= factor

    def translate(self, offset):
        self.x += offset.x
        self.y += offset.y
        self.z += offset.z

    def scale(self, factor):
        self.x *= factor.x
        self.y *= factor.y
        self.z *= factor.z

    def rotate(self, *args):
        """
        Rotates the vector according to the given arguments.

        Supported forms:
        - rotate(direction: Vector3, angle: float)
        - rotate(direction: Vector3, cosine: float, sine: float)
        - rotate(direction: Vector3, up: Vector3, side: Vector3)
        - rotate(orientation: Orientation3)
        - rotate(transformation: Transformation)
        """
        from OpenBveApi.World.Transformations import Transformation
        from OpenBveApi.World.Orientation3 import Orientation3
        if len(args) == 2 and isinstance(args[0], Vector3) and isinstance(args[1], (int, float)):
            # direction, angle
            direction, angle = args
            cosine = math.cos(angle)
            sine = math.sin(angle)
            self.rotate(direction, cosine, sine)

        elif len(args) == 3 and all(isinstance(arg, Vector3) for arg in args):
            # direction, up, side
            direction, up, side = args
            x = side.x * self.x + up.x * self.y + direction.x * self.z
            y = side.y * self.x + up.y * self.y + direction.y * self.z
            z = side.z * self.x + up.z * self.y + direction.z * self.z
            self.x, self.y, self.z = x, y, z


        elif len(args) == 3 and isinstance(args[0], Vector3):

            direction = args[0]

            cosineOfAngle = args[1]

            sineOfAngle = args[2]

            cosineComplement = 1.0 - cosineOfAngle

            x = (cosineOfAngle + cosineComplement * direction.x * direction.x) * self.x + (

                    cosineComplement * direction.x * direction.y - sineOfAngle * direction.z) * self.y + (

                        cosineComplement * direction.x * direction.z + sineOfAngle * direction.y) * self.z

            y = (cosineOfAngle + cosineComplement * direction.y * direction.y) * self.y + (

                    cosineComplement * direction.x * direction.y + sineOfAngle * direction.z) * self.x + (

                        cosineComplement * direction.y * direction.z - sineOfAngle * direction.x) * self.z

            z = (cosineOfAngle + cosineComplement * direction.z * direction.z) * self.z + (

                    cosineComplement * direction.x * direction.z - sineOfAngle * direction.y) * self.x + (

                        cosineComplement * direction.y * direction.z + sineOfAngle * direction.x) * self.y

            self.x = x

            self.y = y

            self.z = z

        elif len(args) == 1 and isinstance(args[0], Orientation3):
            # Rotate by orientation
            o = args[0]
            x = o.x.x * self.x + o.y.x * self.y + o.z.x * self.z
            y = o.x.y * self.x + o.y.y * self.y + o.z.y * self.z
            z = o.x.z * self.x + o.y.z * self.y + o.z.z * self.z
            self.x, self.y, self.z = x, y, z

        elif len(args) == 1 and isinstance(args[0], Transformation):
            # Rotate by transformation
            t = args[0]
            x = t.x.x * self.x + t.y.x * self.y + t.z.x * self.z
            y = t.x.y * self.x + t.y.y * self.y + t.z.y * self.z
            z = t.x.z * self.x + t.y.z * self.y + t.z.z * self.z
            self.x, self.y, self.z = x, y, z

        else:
            raise TypeError("Invalid arguments for rotate()")

    def rotate_with_cos_sin(self, direction, cos_a, sin_a):
        c = 1.0 - cos_a
        x = (cos_a + c * direction.x * direction.x) * self.x + \
            (c * direction.x * direction.y - sin_a * direction.z) * self.y + \
            (c * direction.x * direction.z + sin_a * direction.y) * self.z
        y = (cos_a + c * direction.y * direction.y) * self.y + \
            (c * direction.x * direction.y + sin_a * direction.z) * self.x + \
            (c * direction.y * direction.z - sin_a * direction.x) * self.z
        z = (cos_a + c * direction.z * direction.z) * self.z + \
            (c * direction.x * direction.z - sin_a * direction.y) * self.x + \
            (c * direction.y * direction.z + sin_a * direction.x) * self.y

        self.x, self.y, self.z = x, y, z

    def rotate_plane(self, cosa, sina):
        u = self.x * cosa - self.z * sina
        v = self.x * sina + self.z * cosa
        self.x, self.z = u, v

    def is_null_vector(self):
        return self.x == 0.0 and self.y == 0.0 and self.z == 0.0
