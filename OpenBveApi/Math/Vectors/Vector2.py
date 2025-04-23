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