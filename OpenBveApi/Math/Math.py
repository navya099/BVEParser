import math
import re


class NumberFormats:
    @staticmethod
    def try_parse_double_vb6(expression: str, unit_factors: list[float] = None)\
            -> tuple[bool, float]:
        def parse_single(s: str) -> float | None:
            try:
                return float(s.strip().lower().replace("d", "e"))
            except ValueError:
                return None

        # 기본 값
        value = 0.0

        # 단순한 숫자 하나일 때
        parsed = parse_single(expression)
        if parsed is not None:
            if unit_factors:
                value = parsed * unit_factors[-1]
            else:
                value = parsed
            return True, value

        # 콜론(:) 구분자 있는 복합 형식일 때
        if unit_factors is None:
            return False, 0.0  # 단위 변환 정보 없으면 실패

        parts = expression.split(':')
        if len(parts) > len(unit_factors):
            return False, 0.0

        for i, part in enumerate(parts):
            parsed = parse_single(part)
            if parsed is None:
                return False, 0.0
            j = i + len(unit_factors) - len(parts)
            value += parsed * unit_factors[j]

        return True, value

    @staticmethod
    def try_parse_float_vb6(expression: str) -> tuple[bool, float]:
        """Parses a float formatted as a Visual Basic 6 string."""
        expression = NumberFormats.trim_inside(expression)
        for n in range(len(expression), 0, -1):
            try:
                value = float(expression[:n])
                return True, value
            except ValueError:
                continue
        return False, 0.0

    def try_parse_int_vb6(expression: str) -> tuple[bool, int]:
        """Parses an integer formatted as a Visual Basic 6 string."""
        expression = NumberFormats.trim_inside(expression)
        for n in range(len(expression), 0, -1):
            try:
                value = float(expression[:n])
                if -2147483648 <= value <= 2147483647:
                    return True, round(value)
                break
            except ValueError:
                continue
        return False, 0

    @staticmethod
    def is_valid_double(expression: str, unit_factors: list[float]) -> bool:
        """Returns whether a string contains a valid double with optional unit parsing."""
        success, _ = NumberFormats.try_parse_double(expression, unit_factors)
        return success

    @staticmethod
    def try_parse_double(expression: str, unit_factors: list[float]) -> tuple[bool, float]:
        """Parses a double from a string, supporting colon-separated units."""
        try:
            value = float(expression)
            return True, value * unit_factors[-1]
        except ValueError:
            parts = expression.split(':')
            if len(parts) > len(unit_factors):
                return False, 0.0

            value = 0.0
            for i, part in enumerate(parts):
                try:
                    num = float(part.strip())
                    j = i + len(unit_factors) - len(parts)
                    value += num * unit_factors[j]
                except ValueError:
                    return False, 0.0
            return True, value

    @staticmethod
    def try_parse_double_vb6_units(expression: str, unit_factors: list[float]) -> tuple[bool, float]:
        """Parses a VB6-style double with unit support."""
        try:
            value = float(expression)
            return True, value * unit_factors[-1]
        except ValueError:
            parts = expression.split(':')
            if len(parts) > len(unit_factors):
                return False, 0.0

            value = 0.0
            for i, part in enumerate(parts):
                success, num = NumberFormats.try_parse_double_vb6(part.strip())
                if not success:
                    return False, 0.0
                j = i + len(unit_factors) - len(parts)
                value += num * unit_factors[j]
            return True, value

    @staticmethod
    def to_radians(degrees: float) -> float:
        """Converts degrees to radians."""
        return degrees * (math.pi / 180.0)

    @staticmethod
    def mod(a: float, b: float) -> float:
        """Returns a modulo b."""
        return a - b * math.floor(a / b)

    @staticmethod
    def trim_inside(expression: str) -> str:
        return ''.join(c for c in expression if not c.isspace())
