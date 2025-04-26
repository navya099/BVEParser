from Plugins.RouteCsvRw.RouteData import RouteData
from .Structures.Expression import Expression
from typing import List
from OpenBveApi.Math.Math import NumberFormats
from loggermodule import logger


class Parser2:
    def __init__(self):
        super().__init__()  # 💡 중요!
    def pre_process_options(self, expressions: List[Expression], data: RouteData,
                            unit_of_length: List[float], preview_only: bool) -> RouteData:
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
                command, argument_sequence = expressions[j].separate_commands_and_arguments(None, True, self.IsRW,
                                                                                            section)
                # process command
                number_check = not self.IsRW or section.lower() == "track"

                success, _ = NumberFormats.try_parse_double_vb6(command, unit_of_length)
                if not number_check or not success:
                    # plit arguments
                    arguments = []
                    n = 0
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

                        command = command.replace('.Void', '')

                    # handle indices
                    if command is not None and command.endswith(')'):
                        for k in range(len(command) - 2, -1, -1):
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

                                    logger.error(f'At least 1 argument is expected in {command} at line '
                                          f'{str(expressions[j].Line)}, column {str(expressions[j].Column)} in file '
                                          f'{expressions[j].File}')
                                else:
                                    unit_of_length = []

                                    for i, arg in enumerate(arguments):
                                        # 기본값: 마지막이면 1.0, 아니면 0.0
                                        try:
                                            value = float(arg) if arg.strip() else (
                                                1.0 if i == len(arguments) - 1 else 0.0)
                                        except ValueError:
                                            logger.error(
                                                f"🚫 FactorInMeters{i} is invalid in {command} at line "
                                                f"{expressions[j].Line}, column {expressions[j].Column} in file "
                                                f"{expressions[j].File}")
                                            value = 1.0 if i == 0 else 0.0

                                        if value <= 0.0:
                                            logger.error(
                                                f"⚠️  FactorInMeters{i} is expected to be positive in {command} at line "
                                                f"{expressions[j].Line}, column {expressions[j].Column} in file "
                                                f"{expressions[j].File}")
                                            value = 1.0 if i == len(arguments) - 1 else 0.0

                                        unit_of_length.append(value)

                            case "options.unitofspeed":
                                if len(arguments) < 1:
                                    logger.error(f'Exactly 1 argument is expected in {command} at line '
                                          f'{expressions[j].Line}, column {expressions[j].Column} in file '
                                          f'{expressions[j].File}')
                                else:
                                    if len(arguments) > 1:
                                        logger.warning(f'Exactly 1 argument is expected in {command} at line '
                                              f'{expressions[j].Line}, column {expressions[j].Column} in file '
                                              f'{expressions[j].File}')

                                    suceesss, out = NumberFormats.try_parse_double_vb6(arguments[0])
                                    data.UnitOfSpeed = out
                                    if len(arguments[0]) > 0 and not suceesss:
                                        logger.error(f'Factor InKmph is invalid in {command} at line '
                                              f'{expressions[j].Line}, column {expressions[j].Column} in file '
                                              f'{expressions[j].File}')
                                        data.UnitOfSpeed = 0.277777777777778
                                    elif data.UnitOfSpeed <= 0:
                                        logger.error(f'Factor InKmph is expected to be positive in {command} at line '
                                              '{expressions[j].Line}, column {expressions[j].Column} in file '
                                              f'{expressions[j].File}')
                                        data.UnitOfSpeed = 0.277777777777778

                                    else:
                                        data.UnitOfSpeed *= 0.277777777777778
                            case "options.objectvisibility":
                                if len(arguments) == 0:
                                    logger.error(f'Exactly 1 argument is expected in {command} at line '
                                          f'{expressions[j].Line}, column {expressions[j].Column} in file '
                                          f'{expressions[j].File}')
                                else:
                                    if len(arguments) > 1:
                                        logger.warning(f'Exactly 1 argument is expected in {command} at line '
                                              f'{expressions[j].Line}, column {expressions[j].Column} in file '
                                              f'{expressions[j].File}')

                                    suceesss, mode = NumberFormats.try_parse_int_vb6(arguments[0])
                                    if len(arguments) >= 1 and len(arguments[0]) != 0 and not suceesss:
                                        logger.error(f'Mode is invalid in {command} at line '
                                              f'{expressions[j].Line}, column {expressions[j].Column} in file '
                                              f'{expressions[j].File}')
                                        mode = 0
                                    elif mode < 0 or mode > 2:
                                        logger.error(f'The specified Mode is not supported in {command} at line '
                                              f'{expressions[j].Line}, column {expressions[j].Column} in file '
                                              f'{expressions[j].File}')
                                        mode = 0
                                    self.Plugin.CurrentOptions.ObjectDisposalMode = mode
                            case "options.compatibletransparencymode":
                                '''
                                Whether to use fuzzy matching for BVE2 / BVE4 transparencies
                                Should be DISABLED on openBVE content
                                '''
                                if preview_only:
                                    continue
                                if len(arguments) == 0:
                                    logger.error(f'Exactly 1 argument is expected in {command} at line '
                                          f'{expressions[j].Line}, column {expressions[j].Column} in file '
                                          f'{expressions[j].File}')
                                else:
                                    if len(arguments) > 1:
                                        logger.warning(f'Exactly 1 argument is expected in {command} at line '
                                              f'{expressions[j].Line}, column {expressions[j].Column} in file '
                                              f'{expressions[j].File}')

                                    suceesss, mode = NumberFormats.try_parse_int_vb6(arguments[0])
                                    if len(arguments) >= 1 and len(arguments[0]) != 0 and not suceesss:
                                        logger.error(f'Mode is invalid in {command} at line '
                                              f'{expressions[j].Line}, column {expressions[j].Column} in file '
                                              f'{expressions[j].File}')
                                        mode = 0
                                    elif mode != 0 and mode != 1:
                                        logger.error(f'The specified Mode is not supported in {command} at line '
                                              f'{expressions[j].Line}, column {expressions[j].Column} in file '
                                              f'{expressions[j].File}')
                                        mode = 0
                                    self.Plugin.CurrentOptions.OldTransparencyMode = (mode == 1)
                            case "options.enablebvetshacks":
                                pass
                            case "options.enablehacks":
                                '''
                                Whether to apply various hacks to fix BVE2 / BVE4 routes
                                hilst this is harmless, it should be DISABLED on openBVE content
                                in order to ensure that all errors are correctly fixed by the developer
                                '''
                                if preview_only:
                                    continue
                                if len(arguments) == 0:
                                    logger.error(f'Exactly 1 argument is expected in {command} at line '
                                          f'{expressions[j].Line}, column {expressions[j].Column} in file '
                                          f'{expressions[j].File}')
                                else:
                                    if len(arguments) > 1:
                                        logger.warning(f'Exactly 1 argument is expected in {command} at line '
                                              f'{expressions[j].Line}, column {expressions[j].Column} in file '
                                              f'{expressions[j].File}')
                                    suceesss, mode = NumberFormats.try_parse_int_vb6(arguments[0])
                                    if len(arguments) >= 1 and len(arguments[0]) != 0 and not suceesss:
                                        logger.error(f'Mode is invalid in {command} at line '
                                              f'{expressions[j].Line}, column {expressions[j].Column} in file '
                                              f'{expressions[j].File}')
                                        mode = 0
                                    elif mode != 0 and mode != 1:
                                        logger.error(f'The specified Mode is not supported in {command} at line '
                                              f'{expressions[j].Line}, column {expressions[j].Column} in file '
                                              f'{expressions[j].File}')
                                        mode = 0
                                    self.Plugin.CurrentOptions.EnableBveTsHacks = (mode == 1)
        return data
