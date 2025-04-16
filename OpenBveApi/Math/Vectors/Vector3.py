from dataclasses import dataclass
import math
from typing import List, Tuple


@dataclass
class Vector3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    @property
    def X(self):
        return self.x

    @X.setter
    def X(self, value):
        self.x = value

    @property
    def Y(self):
        return self.y

    @Y.setter
    def Y(self, value):
        self.y = value

    @property
    def Z(self):
        return self.z

    @Z.setter
    def Z(self, value):
        self.z = value

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

    # ✅ 클래스 속성으로 Vector3 인스턴스 지정
    Forward = None
    Backward = None
    Zero = None
    Left = None
    Right = None
    Down = None

    # 벡터 + 벡터
    def __add__(self, other):
        if isinstance(other, Vector3):
            return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
        elif isinstance(other, (int, float)):
            return Vector3(self.x + other, self.y + other, self.z + other)
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
        return hash((self.X, self.Y, self.Z))

    def normalize(self):
        norm = self.X ** 2 + self.Y ** 2 + self.Z ** 2
        if norm == 0.0:
            return
        factor = 1.0 / math.sqrt(norm)
        self.X *= factor
        self.Y *= factor
        self.Z *= factor

    def translate(self, offset):
        self.X += offset.X
        self.Y += offset.Y
        self.Z += offset.Z

    def scale(self, factor):
        self.X *= factor.X
        self.Y *= factor.Y
        self.Z *= factor.Z

    def rotate(self, direction, angle):
        cos_a = math.cos(angle)

        sin_a = math.sin(angle)
        self.rotate_with_cos_sin(direction, cos_a, sin_a)

    def rotate_with_cos_sin(self, direction, cos_a, sin_a):
        c = 1.0 - cos_a
        x = (cos_a + c * direction.X * direction.X) * self.X + \
            (c * direction.X * direction.Y - sin_a * direction.Z) * self.Y + \
            (c * direction.X * direction.Z + sin_a * direction.Y) * self.Z
        y = (cos_a + c * direction.Y * direction.Y) * self.Y + \
            (c * direction.X * direction.Y + sin_a * direction.Z) * self.X + \
            (c * direction.Y * direction.Z - sin_a * direction.X) * self.Z
        z = (cos_a + c * direction.Z * direction.Z) * self.Z + \
            (c * direction.X * direction.Z - sin_a * direction.Y) * self.X + \
            (c * direction.Y * direction.Z + sin_a * direction.X) * self.Y
        self.X, self.Y, self.Z = x, y, z

    def rotate_plane(self, cosa, sina):
        u = self.X * cosa - self.Z * sina
        v = self.X * sina + self.Z * cosa
        self.X, self.Z = u, v

    def is_null_vector(self):
        return self.X == 0.0 and self.Y == 0.0 and self.Z == 0.0


# ✅ 클래스 밖에서 초기화 (dataclass의 제한 피하기 위함)
Vector3.Forward = Vector3(0.0, 0.0, 1.0)
Vector3.Backward = Vector3(0.0, 0.0, -1.0)
Vector3.Zero = Vector3(0.0, 0.0, 0.0)
Vector3.Left = Vector3(-1.0, 0.0, 0.0)
Vector3.Right = Vector3(1.0, 0.0, 0.0)
Vector3.Down = Vector3(0.0, 1.0, 0.0)
Vector3.Up = Vector3(0.0, -1.0, 0.0)
