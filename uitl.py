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

    @staticmethod
    def write_all_lines(path, text_list):
        with open(path, 'w', encoding='utf-8') as f:
            for txt in text_list:
                f.write(txt + '\n')

    @staticmethod
    def test(expressions):
        with open("C:/TEMP/expressions_all.csv", "w", encoding="utf-8-sig") as f:
            f.write(f"인덱스,줄,텍스트,오프셋,파일\n")
            for i, expr in enumerate(expressions):
                f.write(f"{i},{expr.Line},{expr.Text},{expr.TrackPositionOffset},{expr.File}\n")




