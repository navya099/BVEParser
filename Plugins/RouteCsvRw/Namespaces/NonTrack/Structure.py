from Plugins.RouteCsvRw.Namespaces.NonTrack.StructureCommands import StructureCommand
from Plugins.RouteCsvRw.RouteData import RouteData
from Plugins.RouteCsvRw.Structures.Expression import Expression
from loggermodule import logger
from OpenBveApi.System.Path import Path
from Plugins.RouteCsvRw.ObjectDictionary import ObjectDictionary
from OpenBveApi.Routes.ObjectDisposalMode import ObjectDisposalMode


class Parser10:
    def __init__(self):
        super().__init__()

    def parse_structure_command(self, command: StructureCommand, arguments: [str], command_indices: [int]
                                , filename: str, encoding: str, expression: Expression, data: RouteData
                                , preview_only: bool) -> RouteData:
        match command:
            case StructureCommand.Rail:
                if command_indices[0] < 0:
                    logger.error(f'RailStructureIndex is expected to be non-negative in {command} at line '
                                 f'{expression.Line}, column {expression.Column} in file {expression.File}')
                else:

                    if len(arguments) < 1:
                        logger.error(f'{command} is expected to have one argument at line '
                                     f'{expression.Line}, column {expression.Column} in file {expression.File}')
                    elif Path.contains_invalid_chars(arguments[0]):
                        logger.error(f'FileName {arguments[0]} contains illegal characters in {command} at line '
                                     f'{expression.Line}, column {expression.Column} in file {expression.File}')
                    else:
                        f = arguments[0]
                        success, f = self.locate_object(f, self.ObjectPath)
                        if not success:
                            logger.error(f'FileName {f} not found in{command} at line '
                                         f'{expression.Line}, column {expression.Column} in file {expression.File}')
                            self.missingObjectCount += 1
                        else:
                            if not preview_only:
                                # result, obj = self.Plugin.CurrentHost.LoadObject(f, encoding)
                                obj = [f]
                                if obj is not None:
                                    data.Structure.RailObjects.Add(command_indices[0], obj, 'RailStructure')
                            else:
                                self.railtypeCount += 1
            case StructureCommand.Pole:
                if command_indices[0] < 0:
                    logger.error(f'AdditionalRailsCovered is expected to be non-negative in {command} at line '
                                 f'{expression.Line}, column {expression.Column} in file {expression.File}')

                elif command_indices[1] < 0:
                    logger.error(f'PoleStructureIndex is expected to be non-negative in {command} at line '
                                 f'{expression.Line}, column {expression.Column} in file {expression.File}')
                else:
                    if len(arguments) < 1:
                        logger.error(f'{command} is expected to have one argument at line '
                                     f'{expression.Line}, column {expression.Column} in file {expression.File}')

                    elif Path.contains_invalid_chars(arguments[0]):
                        logger.error(f'FileName {arguments[0]} contains illegal characters in {command} at line '
                                     f'{expression.Line}, column {expression.Column} in file {expression.File}')
                    else:
                        if command_indices[0] not in data.Structure.Poles:
                            data.Structure.Poles.Add(command_indices[0], ObjectDictionary())
                        f = arguments[0]
                        success, f = self.locate_object(f, self.ObjectPath)
                        if not success:
                            logger.error(f'FileName {f} not found in{command} at line '
                                         f'{expression.Line}, column {expression.Column} in file {expression.File}')
                            self.missingObjectCount += 1
                        else:
                            #success, obj = self.Plugin.CurrentHost.LoadObject(f, encoding)
                            obj = [f]
                            overwrite_default = True if command_indices[1] >= 0 and command_indices[1] >= 3 else False
                            data.Structure.Poles[command_indices[0]].Add(command_indices[1], obj, overwrite_default)

            case StructureCommand.Object | StructureCommand.FreeObj:
                if command == StructureCommand.Object:
                    self.IsHmmsim = True
                    self.Plugin.CurrentOptions.ObjectDisposalMode = ObjectDisposalMode.Accurate

                if command_indices[0] < 0:
                    logger.error(f'FreeObjStructureIndex is expected to be non-negative in {command} at line '
                                 f'{expression.Line}, column {expression.Column} in file {expression.File}')
                else:
                    if len(arguments) < 1:
                        logger.error(f'{command} is expected to have one argument at line '
                                     f'{expression.Line}, column {expression.Column} in file {expression.File}')

                    elif Path.contains_invalid_chars(arguments[0]):
                        logger.error(f'FileName {arguments[0]} contains illegal characters in {command} at line '
                                     f'{expression.Line}, column {expression.Column} in file {expression.File}')
                    else:
                        f = arguments[0]
                        success, f = self.locate_object(f, self.ObjectPath)
                        if not success:
                            logger.error(f'FileName {f} not found in{command} at line '
                                         f'{expression.Line}, column {expression.Column} in file {expression.File}')
                            self.missingObjectCount += 1
                        else:
                            # obj = self.Plugin.CurrentHost.LoadObject(f, encoding)
                            obj = f
                            if obj is not None:
                                data.Structure.FreeObjects.Add(command_indices[0], obj, 'FreeObject')
                            else:
                                self.freeObjCount += 1

        return data
