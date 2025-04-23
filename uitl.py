from enum import Enum
from typing import Type, Tuple, Optional


class Util:
    @staticmethod
    def try_parse_enum(enum_type: Type[Enum], value: str, ignore_case: bool = True) -> Tuple[Optional[Enum], bool]:
        if ignore_case:
            value = value.strip().replace(" ", "_").upper()
            enum_dict = {name.upper(): member for name, member in enum_type.__members__.items()}
        else:
            enum_dict = enum_type.__members__

        result = enum_dict.get(value, None)
        return result, result is not None
