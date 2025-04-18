from Plugins.RouteCsvRw.RouteData import RouteData
from .Structures.Expression import Expression
from typing import List
from OpenBveApi.Math.Math import NumberFormats


class PreprocessMixin2:
    def __init__(self):
        pass

    def pre_process_options(self, expressions: List[Expression], data: RouteData,
                           unit_of_length: List[float], preview_only: bool) -> None:
        section = ''
        section_always_prefix = False
        # process expressions
        for j in range(len(expressions)):
            if self.IsRW and expressions[j].Text.startswith("[") and expressions[j].Text.endswith("]"):
                section = expressions[j].Text[1:-1].strip()
                if section.lower() == "object":
                    section = "Structure"
                elif section.lower() == "railway":
                    section = "Track"

                section_always_prefix = True
            else:
                expressions[j].convert_rw_to_csv(section, section_always_prefix)
                # separate command and arguments
                command, argument_sequence = expressions[j].separate_commands_and_arguments(None, True, self.IsRW, section)
                # process command
                number_check = not self.IsRW or section.lower() == "track"

                success, _ = NumberFormats.try_parse_double_vb6(command, unit_of_length)
                if not number_check or not success:
                    # plit arguments
                    arguments = []
                    n =0
                    for k in range(len(argument_sequence)):
                        if self.IsRW and argument_sequence[k] == ',':
                            n += 1
                        elif argument_sequence[k] == ';':
                            n += 1
                    a, h = 0, 0
                    for k in range(len(argument_sequence)):
                        if self.IsRW and argument_sequence[k] == ',':
                            arguments.append(argument_sequence[a:k].strip())
                            a = k + 1
                            h += 1
                        elif argument_sequence[k] == ';':
                            arguments.append(argument_sequence[a:k].strip())
                            a = k + 1
                            h += 1
                    if len(argument_sequence) - a > 0:
                        arguments.append(argument_sequence[a:].strip())
                        h += 1
                    # preprocess command
                    if command.lower() == 'with':
                        if len(arguments) >= 1:
                            section = arguments[0]
                            section_always_prefix = False
                        else:
                            section = ''
                            section_always_prefix = False

                        command = None

                    else:
                        if command.startswith('.'):
                            command = section + command
                        elif section_always_prefix:
                            command = section + '.' + command

                        command.replace('.Void', '')

                    # handle indices
                    if command is not None and command.endswith(')'):
                        for k in range(len(command) - 2 , -1, -1):
                            if command[k] == '(':
                                indices = command[k + 1:len(command) - 1].lstrip()
                                command = command[:k].rstrip()
                                h = indices.find(";")
                                if h >= 0:
                                    a = indices[:h].rstrip()
                                    b = indices[h + 1:].lstrip()
                                    success, _ = NumberFormats.try_parse_int_vb6(a)
                                    if len(a) > 0 and not success:
                                        command = None
                                        break
                                    success, _ = NumberFormats.try_parse_int_vb6(b)
                                    if len(b) > 0 and not success:
                                        command = None
                                else:
                                    success, _ = NumberFormats.try_parse_int_vb6(indices)
                                    if len(indices) > 0 and not success:
                                        command = None

                                break
                    # process command
                    if command is not None:
                        match command.lower():
                            # options
                            case 'options.unitoflength':
                                if len(arguments) == 0:
                                    print(f'At least 1 argument is expected in {command} at line '
                                          f'{str(expressions[j].Line)}, column {str(expressions[j].Column)} in file '
                                          f'{expressions[j].File}')
                                else:
                                    unit_of_length = []
                                    for i in range(len(arguments)):
                                        unit_of_length.append[1.0] if i == len(arguments) else 0.0







