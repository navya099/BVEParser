from enum import Enum


class OptionsCommand(Enum):
    BlockLength = 0
    XParser = 1
    ObjParser = 2
    UnitOfLength = 3
    UnitOfSpeed = 4
    ObjectVisibility = 5
    SectionBehavior = 6
    CantBehavior = 7
    FogBehavior = 8
    EnableBveTsHacks = 9
    ReverseDirection = 10
