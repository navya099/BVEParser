from enum import Enum


class ObjectDisposalMode(Enum):
    Legacy = 0
    Accurate = 1
    QuadTree = 2
    Mechanik = 99
