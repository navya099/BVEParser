from OpenBveApi.Math.Math import NumberFormats
from Plugins.RouteCsvRw.Structures.Expression import Expression


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
    def find_indices(command: str, expression):
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
                            print(
                                f"Invalid first index at line {expression.Line}, column {expression.Column} in file {expression.File}")
                            command = ''
                        else:
                            command_indices[0] = val_a

                        success_b, val_b = NumberFormats.try_parse_int_vb6(b)
                        if b and not success_b:
                            print(
                                f"Invalid second index at line {expression.Line}, column {expression.Column} in file {expression.File}")
                            command = ''
                        else:
                            command_indices[1] = val_b
                    else:
                        success, val = NumberFormats.try_parse_int_vb6(indices)
                        if indices and not success:
                            if indices.lower() != 'c' or command.lower() != 'route.comment':
                                print(
                                    f"Invalid index at line {expression.Line}, column {expression.Column} in file {expression.File}")
                                command = ''
                        else:
                            command_indices[0] = val
                    break

        return command_indices
