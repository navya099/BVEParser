from dataclasses import dataclass
import math


@dataclass
class Vector2:
    x: float = 0.0
    y: float = 0.0

    @classmethod
    def Null(cls):
        return cls(0.0, 0.0)

    @classmethod
    def Left(cls):
        return cls(-1.0, 0.0)

    @classmethod
    def Right(cls):
        return cls(1.0, 0.0)

    @classmethod
    def Up(cls):
        return cls(0.0, -1.0)

    @classmethod
    def Down(cls):
        return cls(0.0, 1.0)

    @classmethod
    def One(cls):
        return cls(1.0, 1.0)

    def normalize(self):
        norm = self.x * self.x + self.y * self.y
        if norm == 0.0:
            raise ZeroDivisionError
        else:
            factor = 1.0 / math.sqrt(norm)
            self.x *= factor
            self.y *= factor

    def rotate(self, cosine_of_angle: float, sine_of_angle: float):
        x = cosine_of_angle * self.x - sine_of_angle * self.y
        y = sine_of_angle * self.x + cosine_of_angle * self.y
        self.x = x
        self.y = y

    def __sub__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x - other.x, self.y - other.y)

    def clone(self):
        return Vector2(self.x, self.y)