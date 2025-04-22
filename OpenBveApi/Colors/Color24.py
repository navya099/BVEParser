from dataclasses import dataclass


@dataclass
class Color24:
    R: int
    G: int
    B: int

    @classmethod
    def Grey(cls):
        return cls(128, 128, 128)
