import math
import re
class NumberFormats:
    @staticmethod
    def trim_inside(expression: str) -> str:
        """Remove all whitespace characters from the expression."""
        return ''.join(expression.split())

    @staticmethod
    def TryParseDoubleVb6(expression: str) -> tuple[bool, float]:
        """Parses a double formatted as a Visual Basic 6 string."""
        if not expression:
            return False, 0.0
        
        # Handle EM-DASH (– or —)
        if ord(expression[0]) in [65533, 8212, 8211]:
            expression = '-' + expression[1:]

        expression = trim_inside(expression)

        for n in range(len(expression), 0, -1):
            try:
                value = float(expression[:n])
                return True, value
            except ValueError:
                continue
        return False, 0.0

    @staticmethod
    def try_parse_float_vb6(expression: str) -> tuple[bool, float]:
        """Parses a float formatted as a Visual Basic 6 string."""
        expression = trim_inside(expression)
        for n in range(len(expression), 0, -1):
            try:
                value = float(expression[:n])
                return True, value
            except ValueError:
                continue
        return False, 0.0

    def try_parse_int_vb6(expression: str) -> tuple[bool, int]:
        """Parses an integer formatted as a Visual Basic 6 string."""
        expression = trim_inside(expression)
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
        success, _ = try_parse_double(expression, unit_factors)
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
                success, num = try_parse_double_vb6(part.strip())
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
