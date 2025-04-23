from OpenBveApi.Math.Math import NumberFormats
from Plugins.RouteCsvRw.Structures.Expression import Expression


class Parser4:
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

    def find_indices(self, command: str, expression: Expression):
        command_indices = [0 , 0]
        if command is not None and command.endswith(')'):
            for k in range(len(command) - 2, -1 ,-1):
                if command[k] == '(':
                    indices = command[k + 1 : len(command) - 1].lstrip()
                    command = command[:k].rstrip()
                    h = indices.find(";")
                    if h >= 0:
                        a = indices[:h].rstrip()
                        b = indices[h + 1:].lstrip()

                        success, command_indices[0] = NumberFormats.try_parse_int_vb6(a)
                        if len(a) > 0 and not success:
                            print(f'Invalid first index appeared at line {expression.Line},\
                            column {expression.Column} in file {expression.File}')
                            command = None
                        success, command_indices[1] = NumberFormats.try_parse_int_vb6(b)
                        if len(b) > 0 and not success:
                            print(f'Invalid second index appeared at line {expression.Line},\
                            column {expression.Column} in file {expression.File}')
                            command = None
                        else:
                            success, command_indices[0] = NumberFormats.try_parse_int_vb6(indices)
                            if len(indices) > 0 and not success:
                                if indices.lower() != 'c' or command.lower() == 'route.comment':
                                    # (C) used in route comment to represent copyright symbol, so not an error
                                    print(f'Invalid index appeared at line {expression.Line},\
                                                                column {expression.Column} in file {expression.File}')
                                    command = None
                        break
        return command_indices


