import sys
from enum import Enum
from loggermodule import logger

INT_MAX_VALUE = 2**31 - 1

class Direction(Enum):
    Left = -1
    Both = 0
    Right = 1
    Null = 2
    Invalid = INT_MAX_VALUE


class Parser9:
    def __init__(self):
        super().__init__()

    @staticmethod
    def find_direction(direction: str, command: str, iswalldike: bool, line: str, file: str):
        direction = direction.strip()
        match direction.lower():
            case '-1' | 'L' | 'LEFT':
                return Direction.Left
            case 'B' | 'BOTH' :
                return Direction.Both
            case '+1' | '1' | 'R' | 'RIGHT':
                return Direction.Right
            case '0':
                # BVE is inconsistant: Walls / Dikes use 0 for *both* sides, stations use 0 for none....
                return Direction.Both if iswalldike else Direction.Null
            case 'N' | 'NONE' | 'NEITHER':
                return Direction.Null
            case _:
                logger.error(f'Direction is invalid in {command} at line {line} in file {file}')
                return Direction.Invalid


