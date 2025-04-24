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

    def rotate(self, direction, angle):
        cos_a = math.cos(angle)

        sin_a = math.sin(angle)
        self.rotate_with_cos_sin(direction, cos_a, sin_a)

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
