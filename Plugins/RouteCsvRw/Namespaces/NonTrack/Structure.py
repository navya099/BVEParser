from Plugins.RouteCsvRw.Namespaces.NonTrack.StructureCommands import StructureCommand
from Plugins.RouteCsvRw.RouteData import RouteData
from Plugins.RouteCsvRw.Structures.Expression import Expression
from loggermodule import logger


class Parser10:
    def __init__(self):
        super().__init__()
    def parse_structure_command(command: StructureCommand, arguments: [str], command_indices: [int]
                                , filename: str, encoding: str, expression: Expression, data: RouteData
                                , preview_only: bool) -> RouteData:
        match command:
            case StructureCommand.Rail:
                if command_indices[0] < 0:
                    logger.error(f'RailStructureIndex is expected to be non-negative in {command} at line '
                                 f'{expression.Line}, column {expression.Column} in file {expression.File}')
                else:
                    from OpenBveApi.System.Path import Path
                    if len(arguments) < 1:
                        logger.error(f'{command} is expected to have one argument at line '
                                     f'{expression.Line}, column {expression.Column} in file {expression.File}')
                    elif Path.contains_invalid_chars(arguments[0]):
                        logger.error(f'FileName {arguments[0]} contains illegal characters in {command} at line '
                                     f'{expression.Line}, column {expression.Column} in file {expression.File}')
                    else:
                        f = arguments[0]





