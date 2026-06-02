from OpenBveApi.Math.Math import NumberFormats
from Plugins.RouteCsvRw.Structures.Expression import Expression
from loggermodule import logger
import math


class Parser4:
    def __init__(self):
        super().__init__()  # 💡 중요!

    def split_arguments(self, argument_sequence: str) -> list[str]:
        arguments = []
        a = 0
        for k in range(len(argument_sequence)):
            if (self.IsRW and argument_sequence[k] == ',') or argument_sequence[k] == ';':
                arguments.append(argument_sequence[a:k].strip())
                a = k + 1
        if len(argument_sequence) - a > 0:
            arguments.append(argument_sequence[a:].strip())

        return arguments

    @staticmethod
    def find_indices(command: str, expression: Expression) -> tuple[list[int], str]:
        command_indices = [0, 0]

        if command and command.endswith(")"):
            for k in range(len(command) - 2, -1, -1):
                if k >= len(command):  # 안전 확인
                    continue
                if command[k] == '(':
                    indices = command[k + 1: -1].lstrip()
                    command = command[:k].rstrip()
                    h = indices.find(";")
                    if h >= 0:
                        a = indices[:h].rstrip()
                        b = indices[h + 1:].lstrip()

                        success_a, val_a = NumberFormats.try_parse_int_vb6(a)
                        if a and not success_a:
                            logger.error(
                                f"Invalid first index at line {expression.Line}, column {expression.Column} in file {expression.File}")
                            command = ''
                        else:
                            command_indices[0] = val_a

                        success_b, val_b = NumberFormats.try_parse_int_vb6(b)
                        if b and not success_b:
                            logger.error(
                                f"Invalid second index at line {expression.Line}, column {expression.Column} in file {expression.File}")
                            command = ''
                        else:
                            command_indices[1] = val_b
                    else:
                        success, val = NumberFormats.try_parse_int_vb6(indices)
                        if indices and not success:
                            if indices.lower() != 'c' or command.lower() != 'route.comment':
                                logger.error(
                                    f"Invalid index appeared at line {expression.Line}, column {expression.Column} in file {expression.File}")
                                command = ''
                        else:
                            command_indices[0] = val
                    break

        return command_indices, command

    @staticmethod
    def try_parse_time(expression: str):
        expression = expression.strip()
        if not expression:
            return False, 0.0

        if '.' in expression:
            parts = expression.split('.')
        elif ':' in expression:
            parts = expression.split(':')
        else:
            parts = [expression]

        try:
            if len(parts) == 1:
                h = int(parts[0])
                return True, h * 3600.0

            elif len(parts) == 2:
                h = int(parts[0])
                m = int(parts[1])
                return True, h * 3600.0 + m * 60.0

            elif len(parts) >= 3:
                h = int(parts[0])
                m = int(parts[1])
                # 세 번째는 초(second)로 해석
                s_str = ''.join(parts[2:])  # 소수점 안쪽 이어붙이기
                if s_str.startswith('.'):
                    s_str = s_str[1:]
                s = int(s_str)
                return True, h * 3600.0 + m * 60.0 + s

        except ValueError:
            pass

        return False, 0.0

    @staticmethod
    def normalize(x: float, y: float):
        t = x * x + y * y
        if t != 0.0:
            t = 1.0 / math.sqrt(t)
            x *= t
            y *= t
        return x, y
