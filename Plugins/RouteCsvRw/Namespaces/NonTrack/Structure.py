import os

from OpenBveApi.Routes.StaticBackground import StaticBackground
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

    def parse_structure_command(self, command: StructureCommand, arguments: list[str], command_indices: list[int]
                                , filename: str, encoding: str, expression: Expression, data: RouteData
                                , preview_only: bool):
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
                if not preview_only:
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

            case StructureCommand.Ground:
                if not preview_only:
                    if command_indices[0] < 0:
                        logger.error(
                            f"GroundStructureIndex is expected to be non-negative "
                            f"in {command} at line {expression.Line}, column {expression.Column} in file {expression.File}"
                        )
                    else:
                        if len(arguments) < 1:
                            logger.error(
                                f"{command} is expected to have one argument "
                                f"at line {expression.Line}, column {expression.Column} in file {expression.File}"
                            )
                        elif Path.contains_invalid_chars(arguments[0]):
                            logger.error(
                                f"FileName {arguments[0]} contains illegal characters "
                                f"in {command} at line {expression.Line}, column {expression.Column} in file {expression.File}"
                            )
                        else:
                            f = arguments[0]
                            success, f = self.locate_object(f, self.ObjectPath)
                            if not success:
                                logger.error(
                                    f"FileName {f} not found in {command} "
                                    f"at line {expression.Line}, column {expression.Column} in file {expression.File}"
                                )
                            else:
                                obj = f
                                if obj is not None:
                                    data.Structure.Ground.Add(command_indices[0], obj, "GroundStructure")

            case StructureCommand.DikeL | StructureCommand.DikeR | StructureCommand.WallL | StructureCommand.WallR:
                if not preview_only:
                    if command in (StructureCommand.DikeL, StructureCommand.DikeR):
                        current = "Dike"
                    elif command in (StructureCommand.WallL, StructureCommand.WallR):
                        current = "Wall"
                    else:
                        current = "Unknown"

                    if command_indices[0] < 0:
                        side = "Left" if command in (StructureCommand.DikeL, StructureCommand.WallL) else "Right"
                        logger.error(
                            f'{side} {current}StructureIndex must be non-negative in {command} '
                            f'at line {expression.Line}, column {expression.Column} in file {expression.File}'
                        )
                    else:
                        if len(arguments) < 1:
                            logger.error(
                                f'{command} requires one argument at line {expression.Line}, '
                                f'column {expression.Column} in file {expression.File}'
                            )
                        elif Path.contains_invalid_chars(arguments[0]):
                            logger.error(
                                f'FileName {arguments[0]} contains illegal characters in {command} '
                                f'at line {expression.Line}, column {expression.Column} in file {expression.File}'
                            )
                        else:
                            f = arguments[0]
                            success, f = self.locate_object(f, self.ObjectPath)
                            if not success:
                                logger.error(
                                    f'FileName {f} not found in {command} '
                                    f'at line {expression.Line}, column {expression.Column} in file {expression.File}'
                                )
                            else:
                                obj = f
                                if obj is not None:
                                    if command == StructureCommand.WallL:
                                        data.Structure.WallL[command_indices[0]] = obj
                                    elif command == StructureCommand.WallR:
                                        data.Structure.WallR[command_indices[0]] = obj
                                    elif command == StructureCommand.DikeL:
                                        data.Structure.DikeL[command_indices[0]] = obj
                                    elif command == StructureCommand.DikeR:
                                        data.Structure.DikeR[command_indices[0]] = obj

            case StructureCommand.FormL | StructureCommand.FormR | StructureCommand.FormCL | StructureCommand.FormCR:
                if not preview_only:
                    if command in (StructureCommand.FormL, StructureCommand.FormR):
                        current = "Form"
                    elif command in (StructureCommand.FormCL, StructureCommand.FormCR):
                        current = "FormC"
                    else:
                        current = "Unknown"
                    side = "Left" if command in (StructureCommand.FormL, StructureCommand.FormCL) else "Right"
                    if command_indices[0] < 0:

                        logger.error(
                            f"{side} {current}StructureIndex is expected to be non-negative "
                            f"in {command} at line {expression.Line}, column {expression.Column} in file {expression.File}"
                        )
                    else:
                        if len(arguments) < 1:
                            logger.error(
                                f"{command} is expected to have one argument "
                                f"at line {expression.Line}, column {expression.Column} in file {expression.File}"
                            )
                        elif Path.contains_invalid_chars(arguments[0]):
                            logger.error(
                                f"FileName {arguments[0]} contains illegal characters "
                                f"in {command} at line {expression.Line}, column {expression.Column} in file {expression.File}"
                            )
                        else:
                            f = arguments[0]
                            success, f = self.locate_object(f, self.ObjectPath)
                            if not success:
                                logger.error(
                                    f"FileName {f} not found in {command} "
                                    f"at line {expression.Line}, column {expression.Column} in file {expression.File}"
                                )
                            else:
                                # FormL / FormR → LoadObject
                                # FormCL / FormCR → LoadStaticObject
                                if side in ("Left FormStructure", "Right FormStructure"):
                                    obj = f
                                else:
                                    obj = f

                                if obj is not None:
                                    if command == StructureCommand.FormL:
                                        data.Structure.FormL.Add(command_indices[0], obj, 'Left FormStructure')
                                    elif command == StructureCommand.FormR:
                                        data.Structure.FormR.Add(command_indices[0], obj, 'Right FormStructure')
                                    elif command == StructureCommand.FormCL:
                                        data.Structure.FormCL.Add(command_indices[0], obj, 'Left FormCStructure')
                                    elif command == StructureCommand.FormCR:
                                        data.Structure.FormCR.Add(command_indices[0], obj, 'Right FormCStructure')

            case StructureCommand.RoofL | StructureCommand.RoofR | StructureCommand.RoofCL | StructureCommand.RoofCR:
                if not preview_only:
                    if command in (StructureCommand.RoofL, StructureCommand.RoofR):
                        current = "Roof"
                    elif command in (StructureCommand.RoofCL, StructureCommand.RoofCR):
                        current = "RoofC"
                    else:
                        current = "Unknown"
                    side = "Left" if command in (StructureCommand.RoofL, StructureCommand.RoofCL) else "Right"
                    if command_indices[0] < 0:

                        logger.error(
                            f"{side} {current}StructureIndex is expected to be non-negative "
                            f"in {command} at line {expression.Line}, column {expression.Column} in file {expression.File}"
                        )
                    else:
                        if len(arguments) < 1:
                            logger.error(
                                f"{command} is expected to have one argument "
                                f"at line {expression.Line}, column {expression.Column} in file {expression.File}"
                            )
                        elif Path.contains_invalid_chars(arguments[0]):
                            logger.error(
                                f"FileName {arguments[0]} contains illegal characters "
                                f"in {command} at line {expression.Line}, column {expression.Column} in file {expression.File}"
                            )
                        else:
                            # 인덱스가 0일 때 RW 여부 확인
                            if command_indices[0] == 0:
                                if not self.IsRW:
                                    logger.error(
                                        f"{current}StructureIndex was omitted or is 0 in {command} argument "
                                        f"at line {expression.Line}, column {expression.Column} in file {expression.File}"
                                    )
                                command_indices[0] = 1
                            if command_indices[0] < 0:
                                logger.error(
                                    f"{current}StructureIndex is expected to be non-negative "
                                    f"in {command} argument at line {expression.Line}, column {expression.Column} in file {expression.File}"
                                )
                            else:
                                f = arguments[0]
                                success, f = self.locate_object(f, self.ObjectPath)
                                if not success:
                                    logger.error(
                                        f"FileName {f} not found in {command} "
                                        f"at line {expression.Line}, column {expression.Column} in file {expression.File}"
                                    )
                                else:
                                    if side == "Left":
                                        obj = f
                                    else:
                                        obj = f

                                    if obj is not None:
                                        if command == StructureCommand.RoofL:
                                            data.Structure.RoofL.Add(command_indices[0], obj, 'Left RoofStructure')
                                        elif command == StructureCommand.RoofR:
                                            data.Structure.RoofR.Add(command_indices[0], obj, 'Right RoofStructure')
                                        elif command == StructureCommand.RoofCL:
                                            data.Structure.RoofCL.Add(command_indices[0], obj, 'Left RoofCStructure')
                                        elif command == StructureCommand.RoofCR:
                                            data.Structure.RoofCR.Add(command_indices[0], obj, 'Right RoofCStructure')

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

            case StructureCommand.Background | StructureCommand.Back:
                if not preview_only:
                    if command_indices[0] < 0:
                        logger.error(
                            f"BackgroundTextureIndex is expected to be non-negative "
                            f"at line {expression.Line}, column {expression.Column} in file {expression.File}"
                        )
                    elif len(arguments) < 1:
                        logger.error(
                            f"{command} is expected to have one argument "
                            f"at line {expression.Line}, column {expression.Column} in file {expression.File}"
                        )
                    else:
                        if Path.contains_invalid_chars(arguments[0]):
                            logger.error(
                                f"FileName {arguments[0]} contains illegal characters "
                                f"in {command} at line {expression.Line}, column {expression.Column} in file {expression.File}"
                            )
                        else:
                            # Backgrounds dict 초기화
                            if command_indices[0] not in data.Backgrounds:
                                # 파이선에서는 필요 없어서 StaticBackground 객체 주석
                                #data.Backgrounds[command_indices[0]] = StaticBackground(None, 6, False, self.Plugin.CurrentOptions.ViewingDistance, time=0.0, vao=None)
                                pass
                            f = os.path.join(self.ObjectPath, arguments[0])

                            # Uchibo 호환성 처리
                            if not os.path.exists(f) and arguments[0].lower() in ("back_mt.bmp", "back_mthigh.bmp", "bg_fine.bmp"):
                                pass
                                #파이선에서는 필요 없어서 주석
                                #f = os.path.join(self.Plugin.FileSystem.get_data_folder("Compatibility"), "Uchibo", "Back_Mt.png")

                            # BveTs 호환성 처리
                            if not os.path.exists(f) and self.Plugin.CurrentOptions.EnableBveTsHacks:
                                if arguments[0].lower().startswith("midland suburban line"):
                                    arguments[0] = "Midland Suburban Line Objects" + arguments[0][21:]
                                    f = os.path.join(self.ObjectPath, arguments[0])
                                elif command_indices[0] == 0:
                                    pass
                                    #파이선에서는 필요 없어서 주석
                                    #f = 'os.path.join(self.Plugin.file_system.get_data_folder("Compatibility"),"Uchibo", "Back_Mt.png")'

                            if not os.path.exists(f):
                                logger.error(
                                    f"FileName {f} not found in {command} "
                                    f"at line {expression.Line}, column {expression.Column} in file {expression.File}"
                                )
                            else:
                                #xml 객체 처리이지만 파이선에서는 필요 없음
                                if f.lower().endswith(".xml"):
                                    try:
                                        h = f
                                        data.Backgrounds[command_indices[0]] = h
                                    except Exception:
                                        logger.error(
                                            f"{f} is not a valid background XML in {command} "
                                            f"at line {expression.Line}, column {expression.Column} in file {expression.File}"
                                        )
                                else:
                                    #파이선에서는 검증과정 필요 없이 곧바로 딕셔너리에 f를 집어넣으면 됨
                                    data.Backgrounds[command_indices[0]] = f

                                    """파이선에서는 필요없어서 주석처리
                                    b = data.Backgrounds.get(command_indices[0])
                                    if isinstance(b, StaticBackground):
                                        b.texture = plugin.current_host.register_texture(
                                            f, TextureParameters(None, None)
                                        )
                                        
                                    """