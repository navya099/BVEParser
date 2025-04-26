from Plugins.RouteCsvRw.Namespaces.NonTrack.OptionsCommands import OptionsCommand
from Plugins.RouteCsvRw.RouteData import RouteData
from Plugins.RouteCsvRw.Structures.Expression import Expression
from OpenBveApi.Math.Math import NumberFormats
from loggermodule import logger


class Parser5:
    def __init__(self):
        super().__init__()  # 💡 중요!

    @staticmethod
    def parse_option_command(command: OptionsCommand, arguments: list[str],
                             unit_of_length: [float], expression: Expression,
                             data: RouteData, preview_only: bool) -> RouteData:
        match command:
            case OptionsCommand.BlockLength:
                length = 25.0
                sucess, length = NumberFormats.try_parse_double_vb6(arguments[0])
                if len(arguments) >= 1 and len(arguments[0]) > 1 and not sucess:
                    logger.error(f'Length is invalid in Options.BlockLength at line '
                          f'{expression.Line},\
                            column {expression.Column} in file {expression.File}')
                    length = 25.0

                data.BlockInterval = length
            case OptionsCommand.XParser:
                pass
            case OptionsCommand.ObjParser:
                pass
            case OptionsCommand.UnitOfLength:
                pass
            case OptionsCommand.UnitOfSpeed:
                pass
            case OptionsCommand.ObjectVisibility:
                pass
            case OptionsCommand.SectionBehavior:
                pass
            case OptionsCommand.CantBehavior:
                pass
            case OptionsCommand.FogBehavior:
                pass
            case OptionsCommand.EnableBveTsHacks:
                pass
            case OptionsCommand.ReverseDirection:
                pass

        return data
