from Plugins.RouteCsvRw.Namespaces.Track.TrackCommands import TrackCommand
from Plugins.RouteCsvRw.RouteData import RouteData
from Plugins.RouteCsvRw.Structures.Expression import Expression
from OpenBveApi.Math.Math import NumberFormats
from Plugins.RouteCsvRw.Structures.Route.RailCycle import RailCycle
from Plugins.RouteCsvRw.Structures.Route.StationStop import Stop


import math
import numpy as np

from Plugins.RouteCsvRw.Structures.Route.Rail import Rail
from RouteManager2.Stations.RouteStation import RouteStation
from loggermodule import logger


class Parser7:
    def __init__(self):
        super().__init__()  # 💡 중요!
        self.CurrentStation: int = -1
        self.CurrentStop: int = -1
        self.CurrentSection: int = 0
        self.DepartureSignalUsed: bool = False

    def parse_track_command(self, command: TrackCommand, arguments: list[str], filename: str,
                            unit_of_lngth: list[float], expression: Expression, data: RouteData, block_index: int,
                            preview_only: bool, is_rw: bool, rail_index: int = 0) -> RouteData:
        match command:
            case TrackCommand.RailStart | TrackCommand.Rail:
                idx = 0
                if len(arguments) >= 1 and len(arguments[0]) > 0:
                    sucess, idx = NumberFormats.try_parse_int_vb6(arguments[0])
                    if not sucess:
                        logger.error(f'RailIndex is invalid in {command} at line '
                              f'{expression.Line} , column {expression.Column}'
                              f' in file {expression.File}')
                if idx < 1:
                    logger.error(f'RailIndex is expected to be positive in {command} at line '
                          f'{expression.Line} , column {expression.Column}'
                          f' in file {expression.File}')
                if command == TrackCommand.RailStart:
                    if idx in data.Blocks[block_index].Rails and data.Blocks[block_index].Rails[idx].RailStarted:
                        logger.error(f'RailIndex {idx} is required to reference a non-existing rail in {command} at line '
                              f'{expression.Line} , column {expression.Column} in file {expression.File}')
                if idx not in data.Blocks[block_index].Rails:
                    data.Blocks[block_index].Rails[idx] = Rail(2.0, 1.0)
                    if idx >= len(data.Blocks[block_index].RailCycles):
                        ol = len(data.Blocks[block_index].RailCycles)
                        # 늘려주기
                        data.Blocks[block_index].RailCycles.extend([RailCycle() for _ in range(idx + 1 - ol)])
                        for rc in range(ol, len(data.Blocks[block_index].RailCycles)):
                            data.Blocks[block_index].RailCycles[rc].RailCycleIndex = -1

                current_rail = data.Blocks[block_index].Rails[idx]
                if current_rail.RailStartRefreshed:
                    current_rail.RailEnded = True

                current_rail.RailStarted = True
                current_rail.RailStartRefreshed = True
                if len(arguments) >= 2:
                    if len(arguments[1]) > 0:
                        success, current_rail.RailStart.x = NumberFormats.try_parse_double_vb6(
                            arguments[1], unit_of_lngth
                        )
                        if not success:
                            logger.error(f'X is invalid in {command} at line {expression.Line} , column {expression.Column}'
                                  f'in file {expression.File}')
                            current_rail.RailStart.x = 0.0
                    if not current_rail.RailEnded:
                        current_rail.RailEnd.x = current_rail.RailStart.x

                if len(arguments) >= 3:
                    if len(arguments[2]) > 0:
                        success, current_rail.RailStart.y = NumberFormats.try_parse_double_vb6(
                            arguments[2], unit_of_lngth
                        )
                        if not success:
                            logger.error(f'Y is invalid in {command} at line {expression.Line} , column {expression.Column}'
                                  f'in file {expression.File}')
                            current_rail.RailStart.y = 0.0
                    if not current_rail.RailEnded:
                        current_rail.RailEnd.y = current_rail.RailStart.y

                if idx >= len(data.Blocks[block_index].RailType):
                    data.Blocks[block_index].RailType.extend([0] * (idx + 1 - len(data.Blocks[block_index].RailType)))
                # Ignore the RailStructureIndex in previewmode, obviously not visible!
                sttype = 0
                if not preview_only and len(arguments) >= 4 and len(arguments[3]) != 0:
                    success, sttype = NumberFormats.try_parse_int_vb6(arguments[3])
                    if not success:
                        logger.error(f'RailStructureIndex is invalid in {command} at line {expression.Line} ,'
                              f' column {expression.Column} in file {expression.File}')
                        sttype = 0
                    if sttype < 0:
                        logger.error(
                            f'RailStructureIndex is expected to be non-negative in {command} at line {expression.Line}'
                            f', column {expression.Column} in file {expression.File}')
                        sttype = 0
                    elif sttype in data.Structure.RailObjects:
                        logger.error(
                            f'RailStructureIndex {sttype} references an object not loaded in {command} at line '
                            f'{expression.Line} ,column {expression.Column} in file {expression.File}')
                    else:
                        if sttype < len(data.Structure.RailCycles) and data.Structure.RailCycles[sttype] is not None:
                            data.Blocks[block_index].RailType[idx] = data.Structure.RailCycles[sttype][0]
                            data.Blocks[block_index].RailCycles[idx].RailCycleIndex = sttype
                            data.Blocks[block_index].RailCycles[idx].CurrentCycle = 0

                        else:
                            data.Blocks[block_index].RailType[idx] = sttype
                            data.Blocks[block_index].RailCycles[idx].RailCycleIndex = -1
                cant = 0.0
                if len(arguments) >= 5 and len(arguments[4]) > 0:
                    success, cant = NumberFormats.try_parse_double_vb6(arguments[4])
                    if not success:
                        if arguments[4] != "id 0":  # RouteBuilder inserts these, harmless so let's ignore
                            logger.error(f'CantInMillimeters is invalid in {command} at line {expression.Line}'
                                  f', column {expression.Column} in file {expression.File}')
                        cant = 0.0
                else:
                    cant *= 0.001
                current_rail.CurveCant = cant
                data.Blocks[block_index].Rails[idx] = current_rail
            case TrackCommand.RailEnd:
                idx = 0
                if len(arguments) >= 1 and len(arguments[0]) > 0:
                    sucess, idx = NumberFormats.try_parse_int_vb6(arguments[0])
                    if not sucess:
                        logger.error(f'RailIndex {idx} is invalid in {command} at line '
                              f'{expression.Line} , column {expression.Column}'
                              f' in file {expression.File}')
                if idx == 0:
                    logger.error(f'The command {command} is invalid for Rail 0 at line '
                          f'{expression.Line} , column {expression.Column}'
                          f' in file {expression.File}')
                if idx < 0 or idx not in data.Blocks[block_index].Rails \
                        or not data.Blocks[block_index].Rails[idx].RailStarted:
                    logger.error(f'RailIndex {idx} references a non-existing rail in {command} at line '
                          f'{expression.Line} , column {expression.Column} in file {expression.File}')
                if idx not in data.Blocks[block_index].Rails:
                    data.Blocks[block_index].Rails[idx] = Rail(2.0, 1.0)

                current_rail = data.Blocks[block_index].Rails[idx]
                current_rail.RailStarted = False
                current_rail.RailStartRefreshed = False
                current_rail.RailEnded = False
                current_rail.IsDriveable = False

                if len(arguments) >= 2 and len(arguments[1]) > 0:
                    success, current_rail.RailEnd.x = NumberFormats.try_parse_double_vb6(arguments[1], unit_of_lngth)
                    if not success:
                        logger.error(f'X is invalid in {command} at line {expression.Line} , column {expression.Column}'
                              f'in file {expression.File}')
                        current_rail.RailEnd.x = 0.0

                if len(arguments) >= 3 and len(arguments[2]) > 0:
                    success, current_rail.RailStart.y = NumberFormats.try_parse_double_vb6(arguments[2], unit_of_lngth)
                    if not success:
                        logger.error(f'Y is invalid in {command} at line {expression.Line} , column {expression.Column}'
                              f'in file {expression.File}')
                        current_rail.RailEnd.y = 0.0
                data.Blocks[block_index].Rails[idx] = current_rail
            case TrackCommand.RailType:
                if not preview_only:
                    idx = 0
                    if len(arguments) >= 1 and len(arguments[0]) > 0:
                        sucess, idx = NumberFormats.try_parse_int_vb6(arguments[0])
                        if not sucess:
                            logger.error(f'RailIndex is invalid in {command} at line '
                                  f'{expression.Line} , column {expression.Column} in file {expression.File}')
                            idx = 0
                    sttype = 0
                    if len(arguments) >= 2 and len(arguments[1]) > 0:
                        success, sttype = NumberFormats.try_parse_int_vb6(arguments[1])
                        if not success:
                            logger.error(f'RailStructureIndex is invalid in {command} at line {expression.Line}' 
                                  f'column {expression.Column} in file {expression.File}')
                            sttype = 0
                    if idx < 0:
                        logger.error(
                            f'RailStructureIndex is expected to be non-negative in {command} at line {expression.Line}'
                            f', column {expression.Column} in file {expression.File}')
                    else:
                        if idx not in data.Blocks[block_index].Rails:
                            logger.warning(
                                f'RailIndex {idx} could be out of range in {command} at line {expression.Line}'
                                f', column {expression.Column} in file {expression.File}')
                        if sttype < 0:
                            logger.error(
                                f'RailStructureIndex is expected to be non-negative in {command} at line'
                                f' {expression.Line}, column {expression.Column} in file {expression.File}')
                        elif sttype not in data.Structure.RailObjects:
                            logger.error(f'RailStructureIndex {sttype} references an object not loaded in {command} at line '
                                  f'{expression.Line} , column {expression.Column} in file {expression.File}')
                        else:
                            if len(data.Blocks[block_index].RailType) <= idx:
                                # RailType 확장
                                data.Blocks[block_index].RailType.extend(
                                    [0] * (idx + 1 - len(data.Blocks[block_index].RailType))
                                )

                                # RailCycles 확장
                                old_len = len(data.Blocks[block_index].RailCycles)
                                data.Blocks[block_index].RailCycles.extend(
                                    RailCycle() for _ in range(idx + 1 - old_len)
                                )

                                # 새로 추가된 RailCycles의 RailCycleIndex 초기화
                                for rc in range(old_len, len(data.Blocks[block_index].RailCycles)):
                                    data.Blocks[block_index].RailCycles[rc].RailCycleIndex = -1
                            if sttype < len(data.Structure.RailCycles) and data.Structure.RailCycles[sttype] \
                                    is not None:
                                data.Blocks[block_index].RailType[idx] = data.Structure.RailCycles[sttype][0]
                                data.Blocks[block_index].RailCycles[idx].RailCycleIndex = sttype
                                data.Blocks[block_index].RailCycles[idx].CurrentCycle = 0
                            else:
                                data.Blocks[block_index].RailType[idx] = sttype
                                data.Blocks[block_index].RailCycles[idx].RailCycleIndex = -1
            case TrackCommand.Accuracy:
                pass
            case TrackCommand.Pitch:
                p = 0.0
                if len(arguments) >= 1 and len(arguments[0]) > 0:
                    sucess, p = NumberFormats.try_parse_double_vb6(arguments[0])
                    if not sucess:
                        logger.error(f'ValueInPermille is invalid in {command} at line '
                              f'{expression.Line} , column {expression.Column}'
                              f' in file {expression.File}')
                        p = 0.0
                data.Blocks[block_index].Pitch = 0.001 * p
            case TrackCommand.Curve:
                radius = 0.0
                if len(arguments) >= 1 and len(arguments[0]) > 0:
                    sucess, radius = NumberFormats.try_parse_double_vb6(arguments[0])
                    if not sucess:
                        logger.error(f'Radius is invalid in {command} at line '
                              f'{expression.Line} , column {expression.Column}'
                              f' in file {expression.File}')
                        radius = 0.0
                cant = 0.0
                if len(arguments) >= 2 and len(arguments[1]) > 0:
                    sucess, cant = NumberFormats.try_parse_double_vb6(arguments[1])
                    if not sucess:
                        logger.error(f'CantInMillimeters is invalid in {command} at line '
                              f'{expression.Line} , column {expression.Column}'
                              f' in file {expression.File}')
                        cant = 0.0
                else:
                    cant *= 0.001
                if data.SignedCant:
                    if radius != 0.0:
                        cant *= np.sign(radius)
                else:
                    cant = abs(cant) * np.sign(radius)
                data.Blocks[block_index].CurrentTrackState.CurveRadius = radius
                data.Blocks[block_index].CurrentTrackState.CurveCant = cant
                data.Blocks[block_index].CurrentTrackState.CurveCantTangent = 0.0

            case TrackCommand.Turn:
                pass
            case TrackCommand.Adhesion:
                pass
            case TrackCommand.Brightness:
                pass
            case TrackCommand.Fog:
                pass
            case TrackCommand.Section:
                pass
            case TrackCommand.SectionS:
                pass
            case TrackCommand.SigF:
                pass
            case TrackCommand.Signal:
                pass
            case TrackCommand.Sig:
                pass
            case TrackCommand.Relay:
                pass
            case TrackCommand.Destination:
                pass
            case TrackCommand.Beacon:
                pass
            case TrackCommand.Transponder:
                pass
            case TrackCommand.Tr:
                pass
            case TrackCommand.ATSSn:
                pass
            case TrackCommand.ATSP:
                pass
            case TrackCommand.Pattern:
                pass
            case TrackCommand.PLimit:
                pass
            case TrackCommand.Limit:
                pass
            case TrackCommand.Stop | TrackCommand.StopPos:
                if self.CurrentStation == -1:
                    logger.error(f"A stop without a station is invalid in Track.Stop at line "
                          f'{expression.Line} , column {expression.Column} in file {expression.File}')
                else:
                    # Direction
                    dir = 0
                    if len(arguments) >= 1 and arguments[0]:
                        success, dir = NumberFormats.try_parse_int_vb6(arguments[0])
                        if not success:
                            logger.error(f"Direction is invalid in Track.Stop at line "
                                  f'{expression.Line} , column {expression.Column} in file {expression.File}')
                            dir = 0

                    # Backward Tolerance
                    backw = 5.0
                    if len(arguments) >= 2 and arguments[1]:
                        success, backw_val = NumberFormats.try_parse_double_vb6(arguments[1], unit_of_lngth)
                        if not success:
                            logger.error(f"BackwardTolerance is invalid in Track.Stop at line"
                                  f'{expression.Line} , column {expression.Column} in file {expression.File}')
                        elif backw_val <= 0.0:
                            logger.error(f"BackwardTolerance is expected to be positive in Track.Stop at line"
                                  f'{expression.Line} , column {expression.Column} in file {expression.File}')
                        else:
                            backw = backw_val

                    # Forward Tolerance
                    forw = 5.0
                    if len(arguments) >= 3 and arguments[2]:
                        success, forw_val = NumberFormats.try_parse_double_vb6(arguments[2], unit_of_lngth)
                        if not success:
                            logger.error(f"ForwardTolerance is invalid in Track.Stop at line"
                                  f'{expression.Line} , column {expression.Column} in file {expression.File}')
                        elif forw_val <= 0.0:
                            logger.error(f"ForwardTolerance is expected to be positive in Track.Stop at line "
                                  f'{expression.Line} , column {expression.Column} in file {expression.File}')
                        else:
                            forw = forw_val

                    # Cars
                    cars = 0
                    if len(arguments) >= 4 and arguments[3]:
                        success, cars_val = NumberFormats.try_parse_int_vb6(arguments[3])
                        if not success:
                            logger.error("Cars is invalid in Track.Stop at line "
                                  f'{expression.Line} , column {expression.Column} in file {expression.File}')
                        else:
                            cars = cars_val

                    # Append Stop

                    stop = Stop(data.TrackPosition, self.CurrentStation, dir, forw, backw, cars)
                    data.Blocks[block_index].StopPositions.append(stop)
                    self.CurrentStop = cars

            case TrackCommand.Sta:
                self.CurrentStation += 1

                # Station 리스트가 존재하지 않거나 부족할 경우 확장
                if len(self.CurrentRoute.Stations) <= self.CurrentStation:
                    self.CurrentRoute.Stations.append(RouteStation())
                else:
                    self.CurrentRoute.Stations[self.CurrentStation] = RouteStation()

                # 인자가 있으면 이름 지정
                if len(arguments) >= 1 and arguments[0]:
                    self.CurrentRoute.Stations[self.CurrentStation].Name = arguments[0]

            case TrackCommand.Station:
                pass
            case TrackCommand.StationXML:
                pass
            case TrackCommand.Buffer:
                pass
            case TrackCommand.Form:
                pass
            case TrackCommand.Pole:
                pass
            case TrackCommand.PoleEnd:
                pass
            case TrackCommand.Wall:
                pass
            case TrackCommand.WallEnd:
                pass
            case TrackCommand.Dike:
                pass
            case TrackCommand.DikeEnd:
                pass
            case TrackCommand.Marker:
                pass
            case TrackCommand.TextMarker:
                pass
            case TrackCommand.Height:
                if not preview_only:
                    h = 0.0
                    if len(arguments) >= 1 and len(arguments[0]) > 0:
                        success, h = NumberFormats.try_parse_double_vb6(arguments[0], unit_of_lngth)
                        if not success:
                            print(f'Height is invalid in Track.Height at line '
                                  f'{expression.Line} , column {expression.Column}'
                                  f' in file {expression.File}')
                            h = 0.0
                    data.Blocks[block_index].Height = h + 0.3 if is_rw else h
            case TrackCommand.Ground:
                pass
            case TrackCommand.Crack:
                pass
            case TrackCommand.FreeObj:
                pass
            case TrackCommand.Back:
                pass
            case TrackCommand.Background:
                pass
            case TrackCommand.Announce:
                pass
            case TrackCommand.AnnounceAll:
                pass
            case TrackCommand.Doppler:
                pass
            case TrackCommand.DopplerAll:
                pass
            case TrackCommand.MicSound:
                pass
            case TrackCommand.PreTrain:
                pass
            case TrackCommand.PointOfInterest:
                pass
            case TrackCommand.POI:
                pass
            case TrackCommand.HornBlow:
                pass
            case TrackCommand.Rain:
                pass
            case TrackCommand.Snow:
                pass
            case TrackCommand.DynamicLight:
                pass
            case TrackCommand.DirectionalLight:
                pass
            case TrackCommand.AmbientLight:
                pass
            case TrackCommand.LightDirection:
                pass
            case TrackCommand.PatternObj:
                pass
            case TrackCommand.PatternEnd:
                pass
            case TrackCommand.Switch:
                pass
            case TrackCommand.SwitchT:
                pass
            case TrackCommand.PlayerPath:
                pass
            case TrackCommand.RailLimit:
                pass
            case TrackCommand.RailBuffer:
                pass
            case TrackCommand.RailAccuracy:
                pass
            case TrackCommand.RailAdhesion:
                pass
        return data
