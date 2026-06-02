from Plugins.RouteCsvRw.Namespaces.NonTrack.RouteCommands import RouteCommand
from Plugins.RouteCsvRw.RouteData import RouteData
from Plugins.RouteCsvRw.Structures.Expression import Expression
from OpenBveApi.Math.Math import NumberFormats
from loggermodule import logger


class Parser6:
    def __init__(self):
        super().__init__()  # 💡 중요!

    def parse_route_command(self, command: RouteCommand, arguments: list[str], index: int, filename: str,
                            unit_of_length: list[float], expression: 'Expression', data: RouteData,
                            preview_only: bool) -> RouteData:
        match command:
            case RouteCommand.DeveloperID:
                pass
            case RouteCommand.Comment:
                if len(arguments) < 1:
                    logger.error(f'{command} is expected to have one argument at line {expression.Line},\
                            column {expression.Column} in file {expression.File}')
                else:
                    self.CurrentRoute.Comment = arguments[0]
            case RouteCommand.Image:
                pass
            case RouteCommand.TimeTable:
                pass
            case RouteCommand.Change:
                pass
            case RouteCommand.Gauge:
                pass
            case RouteCommand.Signal:
                pass
            case RouteCommand.AccelerationDueToGravity:
                pass
            case RouteCommand.StartTime:
                pass
            case RouteCommand.LoadingScreen:
                pass
            case RouteCommand.DisplaySpeed:
                pass
            case RouteCommand.Briefing:
                pass
            case RouteCommand.Elevation:
                if len(arguments) < 1:
                    logger.error(f'{command} is expected to have one argument at line {expression.Line},\
                                column {expression.Column} in file {expression.File}')
                else:

                    success , a = NumberFormats.try_parse_double_vb6(arguments[0], unit_of_length)
                    if not success:
                        logger.error(f'Height is invalid in {command} at line {expression.Line},\
                                column {expression.Column} in file {expression.File}')

                    else:
                        self.CurrentRoute.Atmosphere.InitialElevation = a
            case RouteCommand.PositionX:
                if len(arguments) < 1:
                    logger.error(f'{command} is expected to have one argument at line {expression.Line},\
                                    column {expression.Column} in file {expression.File}')
                else:

                    success, sf = NumberFormats.try_parse_double_vb6(arguments[0], unit_of_length)
                    if not success:
                        logger.error(f'PositionX is invalid in {command} at line {expression.Line},\
                                    column {expression.Column} in file {expression.File}')

                    else:
                        self.CurrentRoute.Atmosphere.InitialX = sf
            case RouteCommand.PositionY:
                if len(arguments) < 1:
                    logger.error(f'{command} is expected to have one argument at line {expression.Line},\
                                                column {expression.Column} in file {expression.File}')
                else:

                    success, cerc = NumberFormats.try_parse_double_vb6(arguments[0], unit_of_length)
                    if not success:
                        logger.error(f'PositionY is invalid in {command} at line {expression.Line},\
                                                column {expression.Column} in file {expression.File}')

                    else:
                        self.CurrentRoute.Atmosphere.InitialY = cerc
            case RouteCommand.Direction:
                if len(arguments) < 1:
                    logger.error(f'{command} is expected to have one argument at line {expression.Line},\
                                                            column {expression.Column} in file {expression.File}')
                else:

                    success, cerc = NumberFormats.try_parse_double_vb6(arguments[0], unit_of_length)
                    if not success:
                        logger.error(f'Direction is invalid in {command} at line {expression.Line},\
                                                            column {expression.Column} in file {expression.File}')

                    else:
                        self.CurrentRoute.Atmosphere.InitialDirection = cerc
            case RouteCommand.Temperature:
                pass
            case RouteCommand.Pressure:
                pass
            case RouteCommand.AmbientLight:
                pass
            case RouteCommand.DirectionalLight:
                pass
            case RouteCommand.LightDirection:
                pass
            case RouteCommand.DynamicLight:
                pass
            case RouteCommand.InitialViewPoint:
                pass
            case RouteCommand.TfoXML:
                pass
        return data
