from OpenBveApi.Runtime.Route.Station import StationStopMode, StationType
from Plugins.RouteCsvRw.Functions import Parser4
from Plugins.RouteCsvRw.Namespaces.Track.TrackCommands import TrackCommand
from Plugins.RouteCsvRw.RouteData import RouteData
from Plugins.RouteCsvRw.Structures.Expression import Expression
from OpenBveApi.Math.Math import NumberFormats
from Plugins.RouteCsvRw.Structures.Route.FreeObject import FreeObj
from Plugins.RouteCsvRw.Structures.Route.Pole import Pole
from Plugins.RouteCsvRw.Structures.Route.RailCycle import RailCycle
from Plugins.RouteCsvRw.Structures.Route.StationStop import Stop
from Plugins.RouteCsvRw.Structures.Direction import Direction
from Plugins.RouteCsvRw.Structures.Route.Rail import Rail
from Plugins.RouteCsvRw.Structures.Trains.StopRequest import StopRequest
from RouteManager2.SignalManager.SafetySystems import SafetySystem
from RouteManager2.Stations.RouteStation import RouteStation
from OpenBveApi.System.Path import Path

import math
import numpy as np
import os

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
                        return data
                if idx < 1:
                    logger.error(f'RailIndex is expected to be positive in {command} at line '
                                 f'{expression.Line} , column {expression.Column}'
                                 f' in file {expression.File}')
                    return data
                if command == TrackCommand.RailStart:
                    if idx in data.Blocks[block_index].Rails and data.Blocks[block_index].Rails[idx].RailStarted:
                        logger.error(
                            f'RailIndex {idx} is required to reference a non-existing rail in {command} at line '
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
                            logger.error(
                                f'X is invalid in {command} at line {expression.Line} , column {expression.Column}'
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
                            logger.error(
                                f'Y is invalid in {command} at line {expression.Line} , column {expression.Column}'
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
                    elif sttype not in data.Structure.RailObjects:
                        logger.error(
                            f'RailStructureIndex {sttype} references an object not loaded in {command} at line '
                            f'{expression.Line} ,column {expression.Column} in file {expression.File}')
                    else:
                        if sttype < len(data.Structure.RailCycles) and data.Structure.RailCycles[sttype]:
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
                current_rail.raaaaa = True
            case TrackCommand.RailEnd:
                idx = 0
                if len(arguments) >= 1 and len(arguments[0]) > 0:
                    sucess, idx = NumberFormats.try_parse_int_vb6(arguments[0])
                    if not sucess:
                        logger.error(f'RailIndex {idx} is invalid in {command} at line '
                                     f'{expression.Line} , column {expression.Column}'
                                     f' in file {expression.File}')
                        return data
                if idx == 0:
                    logger.error(f'The command {command} is invalid for Rail 0 at line '
                                 f'{expression.Line} , column {expression.Column}'
                                 f' in file {expression.File}')
                    return data
                if idx < 0 or idx not in data.Blocks[block_index].Rails \
                        or not data.Blocks[block_index].Rails[idx].RailStarted:
                    logger.error(f'RailIndex {idx} references a non-existing rail in {command} at line '
                                 f'{expression.Line} , column {expression.Column} in file {expression.File}')
                    return data
                if idx not in data.Blocks[block_index].Rails:
                    data.Blocks[block_index].Rails[idx] = Rail(2.0, 1.0)

                current_rail = data.Blocks[block_index].Rails[idx]
                current_rail.RailStarted = False
                current_rail.RailStartRefreshed = False
                current_rail.RailEnded = True
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
                current_rail.raaaaa = False
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
                        if idx not in data.Blocks[block_index].Rails or not \
                                data.Blocks[block_index].Rails[idx].RailStarted:
                            logger.warning(
                                f'RailIndex {idx} could be out of range in {command} at line {expression.Line}'
                                f', column {expression.Column} in file {expression.File}')
                        if sttype < 0:
                            logger.error(
                                f'RailStructureIndex is expected to be non-negative in {command} at line'
                                f' {expression.Line}, column {expression.Column} in file {expression.File}')
                        elif sttype not in data.Structure.RailObjects:
                            logger.error(
                                f'RailStructureIndex {sttype} references an object not loaded in {command} at line '
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
                            if sttype < len(data.Structure.RailCycles) and data.Structure.RailCycles[sttype]:
                                data.Blocks[block_index].RailType[idx] = data.Structure.RailCycles[sttype][0]
                                data.Blocks[block_index].RailCycles[idx].RailCycleIndex = sttype
                                data.Blocks[block_index].RailCycles[idx].CurrentCycle = 0
                            else:
                                data.Blocks[block_index].RailType[idx] = sttype
                                data.Blocks[block_index].RailCycles[idx].RailCycleIndex = -1
                current_rail = data.Blocks[block_index].Rails[idx]
                current_rail.raaaaa = True
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

                arr = -1.0
                dep = -1.0
                if len(arguments) >= 2 and arguments[1].strip():
                    arg = arguments[1].strip()

                    if arg.lower() in ("p", "l"):
                        self.CurrentRoute.Stations[self.CurrentStation].StopMode = StationStopMode.AllPass

                    elif arg.lower() == "b":
                        self.CurrentRoute.Stations[self.CurrentStation].StopMode = StationStopMode.PlayerPass

                    elif arg.lower().startswith("b:"):
                        self.CurrentRoute.Stations[self.CurrentStation].StopMode = StationStopMode.PlayerPass
                        sucess, arr = self.try_parse_time(arg[2:].strip())
                        if not sucess:
                            logger.error(f"ArrivalTime is invalid in Track.Sta at line "
                                         f"{expression.Line}, column {expression.Column}, file {expression.File}")
                            arr = -1.0

                    elif arg.lower() == "s":
                        self.CurrentRoute.Stations[self.CurrentStation].StopMode = StationStopMode.PlayerStop

                    elif arg.lower().startswith("s:"):
                        self.CurrentRoute.Stations[self.CurrentStation].StopMode = StationStopMode.PlayerStop
                        sucess, arr = self.try_parse_time(arg[2:].strip())
                        if not sucess:
                            logger.error(f"ArrivalTime is invalid in Track.Sta at line "
                                         f"{expression.Line}, column {expression.Column}, file {expression.File}")
                            arr = -1.0

                    elif len(arg) == 1 and arg == '.':
                        pass  # Treat a single period as blank

                    elif arg.lower() == "d":
                        self.CurrentRoute.Stations[self.CurrentStation].Dummy = True

                    else:
                        sucess, arr = self.try_parse_time(arg)
                        if not sucess:
                            logger.error(f"ArrivalTime is invalid in Track.Sta at line "
                                         f"{expression.Line}, column {expression.Column}, file {expression.File}")
                            arr = -1.0

                if len(arguments) >= 3 and arguments[2].strip():
                    arg = arguments[2].strip()

                    if arg.lower() in ("t", "="):
                        self.CurrentRoute.Stations[self.CurrentStation].Type = StationType.Terminal

                    elif arg.lower().startswith("t:"):
                        self.CurrentRoute.Stations[self.CurrentStation].Type = StationType.Terminal
                        success, dep = self.try_parse_time(arg[2:].strip())
                        if not success:
                            logger.error(f"DepartureTime is invalid in Track.Sta at line {expression.Line},"
                                         f"column {expression.Column} in file {expression.File}")
                            dep = -1.0

                    elif arg.lower() == "c":
                        self.CurrentRoute.Stations[self.CurrentStation].Type = StationType.ChangeEnds

                    elif arg.lower().startswith("c:"):
                        self.CurrentRoute.Stations[self.CurrentStation].Type = StationType.ChangeEnds
                        success, dep = self.try_parse_time(arg[2:].strip())
                        if not success:
                            logger.error(f"DepartureTime is invalid in Track.Sta at line {expression.Line},"
                                         f"column {expression.Column} in file {expression.File}")
                            dep = -1.0

                    elif arg.lower().startswith("j:"):
                        split_string = arg.split(':')
                        for i, part in enumerate(split_string):
                            if i == 1:
                                success, jump_index = NumberFormats.try_parse_int_vb6(part.strip())
                                if not success:
                                    logger.error(f"JumpStationIndex is invalid in Track.Sta at line {expression.Line}"
                                                 f", column {expression.Column} in file {expression.File}")
                                    dep = -1.0
                                else:
                                    self.CurrentRoute.Stations[self.CurrentStation].JumpIndex = jump_index
                                    self.CurrentRoute.Stations[self.CurrentStation].Type = StationType.Jump
                            elif i == 2:
                                success, dep = self.try_parse_time(part.strip())
                                if not success:
                                    logger.error(f"DepartureTime is invalid in Track.Sta at line {expression.Line},"
                                                 f"column {expression.Column} in file {expression.File}")
                                    dep = -1.0

                    elif len(arg) == 1 and arg == '.':
                        pass  # treat single period as blank

                    else:
                        success, dep = self.try_parse_time(arg)
                        if not success:
                            logger.error(f"DepartureTime is invalid in Track.Sta at line {expression.Line},"
                                         f"column {expression.Column} in file {expression.File}")
                            dep = -1.0
                passalarm = 0
                if len(arguments) > 4 and len(arguments[3]) > 0:
                    success, passalarm = NumberFormats.try_parse_int_vb6(arguments[3])
                    if not success:
                        logger.error(f"PassAlarm is invalid in Track.Sta at line {expression.Line},"
                                     f"column {expression.Column} in file {expression.File}")
                        passalarm = 0

                door = Direction.Both
                if len(arguments) > 5 and len(arguments[4]) > 0:
                    door = self.find_direction(arguments[4], "Track.Sta", False, expression.Line, expression.File)
                    if door == Direction.Invalid:
                        door = Direction.Both
                stop = 0
                if len(arguments) > 6 and len(arguments[5]) > 0:
                    success, stop = NumberFormats.try_parse_int_vb6(arguments[5])
                    if not success:
                        logger.error(f"ForcedRedSignal is invalid in Track.Sta at line {expression.Line},"
                                     f"column {expression.Column} in file {expression.File}")
                        stop = 0
                device = 0
                if len(arguments) >= 7 and len(arguments[6]) > 0:
                    if arguments[6].lower() == 'ats':
                        device = 0
                    elif arguments[6].lower() == 'atc':
                        device = 1
                    else:
                        success, device = NumberFormats.try_parse_int_vb6(arguments[6])
                        if not success:
                            logger.error(f'System is invalid in Track.Sta at line {expression.Line},'
                                         f"column {expression.Column} in file {expression.File}")
                            device = 0
                    if device != 0 and device != 1:
                        logger.error(f'System is not supported in Track.Sta at line {expression.Line},'
                                     f"column {expression.Column} in file {expression.File}")
                        device = 0
                arrsnd = None
                depsnd = None

                if not preview_only:
                    if len(arguments) >= 8 and len(arguments[7]) > 0:

                        if Path.contains_invalid_chars(arguments[7]):
                            logger.error(f'ArrivalSound contains illegal characters in {expression.Line},'
                                         f"column {expression.Column} in file {expression.File}")
                        else:

                            f = os.path.join(self.SoundPath, arguments[7])
                            if not os.path.exists(f):
                                logger.error(f'ArrivalSound {f} not found in Track.Sta at line {expression.Line},'
                                             f"column {expression.Column} in file {expression.File}")
                            else:
                                radius = 30.0
                                arrsnd = self.Plugin.CurrentHost.register_sound(f, radius)
                halt = 15.0
                if len(arguments) >= 9 and len(arguments[8]) > 0:
                    success, halt = NumberFormats.try_parse_double_vb6(arguments[8])
                    if not success:
                        logger.error(f'StopDuration is invalid in Track.Sta at line {expression.Line},'
                                     f"column {expression.Column} in file {expression.File}")
                        halt = 15.0
                elif halt < 0:
                    logger.error(
                        f'StopDuration is expected to be non-negative in Track.Sta at line  {expression.Line},'
                        f"column {expression.Column} in file {expression.File}")
                elif halt < 5.0:
                    halt = 5.0
                jam = 100.0
                if len(arguments) >= 10 and len(arguments[9]) > 0:
                    success, jam = NumberFormats.try_parse_double_vb6(arguments[8])
                    if not success:
                        logger.error(f'PassengerRatio is invalid in Track.Sta at line {expression.Line},'
                                     f"column {expression.Column} in file {expression.File}")
                        jam = 100.0
                    elif jam < 0.0:
                        logger.error(f'PassengerRatio is expected to be non-negative in Track.Sta at line '
                                     f'{expression.Line},column {expression.Column} in file {expression.File}')

                        jam = 100.0

                if not preview_only:
                    if len(arguments) >= 11 and len(arguments[10]) > 0:
                        if Path.contains_invalid_chars(arguments[10]):
                            logger.error(f'DepartureSound contains illegal characters in {command} at line '
                                         f'{expression.Line},column {expression.Column} in file {expression.File}')
                        else:
                            f = os.path.join(self.SoundPath, arguments[10])
                            if not os.path.exists(f):
                                logger.error(f'DepartureSound {f} not found in Track.Sta at line {expression.Line},'
                                             f"column {expression.Column} in file {expression.File}")
                            else:
                                radius = 30.0
                                arrsnd = self.Plugin.CurrentHost.register_sound(f, radius)
                tdt, tnt = None, None
                if not preview_only:
                    ttidx = 0
                    if len(arguments) >= 12 and len(arguments[11]) > 0:
                        success, ttidx = NumberFormats.try_parse_int_vb6(arguments[11])
                        if not success:
                            ttidx = -1
                        else:
                            if ttidx < 0:
                                logger.error(f'TimetableIndex is expected to be non-negative in Track.Sta at line '
                                             f"{expression.Line}, column {expression.Column} in file {expression.File}")
                                ttidx = -1
                            elif ttidx >= len(data.TimetableDaytime) and ttidx >= len(data.TimetableNighttime):
                                logger.error(f'TimetableIndex references textures not loaded in Track.Sta at line '
                                             f"{expression.Line}, column {expression.Column} in file {expression.File}")
                                ttidx = -1
                            # Assuming Data.TimetableDaytime and Data.TimetableNighttime are lists or similar data
                            # structures
                            tdt = data.TimetableDaytime[ttidx] if 0 <= ttidx < len(data.TimetableDaytime) else None
                            tnt = data.TimetableNighttime[ttidx] if 0 <= ttidx < len(data.TimetableNighttime) else None
                            ttidx = 0
                    else:
                        ttidx = -1
                    if ttidx == -1:
                        if self.CurrentStation > 0:
                            tdt = self.CurrentRoute.Stations[self.CurrentStation - 1].TimetableDaytimeTexture
                            tnt = self.CurrentRoute.Stations[self.CurrentStation - 1].TimetableNighttimeTexture

                        elif len(data.TimetableDaytime) > 0 and len(data.TimetableNighttime) > 0:
                            tdt = data.TimetableDaytime[0]
                            tnt = data.TimetableNighttime[0]
                        else:
                            tdt = None
                            tnt = None

                reopen_door = 0.0
                if not preview_only:
                    if len(arguments) >= 13 and len(arguments[12]) > 0:
                        success, reopen_door = NumberFormats.try_parse_double_vb6(arguments[12])
                        if not success:
                            logger.error(f'ReopenDoor is invalid in Track.Sta at line '
                                         f"{expression.Line}, column {expression.Column} in file {expression.File}")

                            reopen_door = 0.0
                        elif reopen_door < 0.0:
                            logger.error(f'ReopenDoor is expected to be non-negative in Track.Sta at line '
                                         f"{expression.Line}, column {expression.Column} in file {expression.File}")

                            reopen_door = 0.0
                reopen_station_limit = 0
                if not preview_only:
                    if len(arguments) >= 14 and len(arguments[13]) > 0:
                        success, reopen_station_limit = NumberFormats.try_parse_int_vb6(arguments[13])
                        if not success:
                            logger.error(f'ReopenStationLimit is invalid in Track.Sta at line '
                                         f"{expression.Line}, column {expression.Column} in file {expression.File}")

                            reopen_station_limit = 0
                    elif reopen_station_limit < 0:
                        logger.error(f'ReopenStationLimit is expected to be non-negative in Track.Sta at line '
                                     f"{expression.Line}, column {expression.Column} in file {expression.File}")

                        reopen_station_limit = 0

                interference_in_door = self.Plugin.RandomNumberGenerator.random() * 30.0
                if not preview_only:
                    if len(arguments) >= 15 and len(arguments[14]) > 0:
                        success, interference_in_door = NumberFormats.try_parse_double_vb6(arguments[14])
                        if not success:
                            logger.error(f'InterferenceInDoor is invalid in Track.Sta at line '
                                         f"{expression.Line}, column {expression.Column} in file {expression.File}")

                            interference_in_door = self.Plugin.RandomNumberGenerator.random() * 30.0
                    elif interference_in_door < 0.0:
                        logger.error(f'InterferenceInDoor is expected to be non-negative in Track.Sta at line '
                                     f"{expression.Line}, column {expression.Column} in file {expression.File}")

                        interference_in_door = 0.0

                max_interfering_object_rate = self.Plugin.RandomNumberGenerator.randint(1, 99)
                if not preview_only:
                    if len(arguments) >= 16 and len(arguments[15]) > 0:
                        success, max_interfering_object_rate = NumberFormats.try_parse_int_vb6(arguments[15])
                        if not success:
                            logger.error(f'MaxInterferingObjectRate is invalid in Track.Sta at line '
                                         f"{expression.Line}, column {expression.Column} in file {expression.File}")

                            max_interfering_object_rate = self.Plugin.RandomNumberGenerator.randint(1, 99)
                    elif max_interfering_object_rate <= 0 or max_interfering_object_rate >= 100:
                        logger.error(f'MaxInterferingObjectRate is expected to be non-negative in Track.Sta at line '
                                     f"{expression.Line}, column {expression.Column} in file {expression.File}")

                        max_interfering_object_rate = self.Plugin.RandomNumberGenerator.randint(1, 99)
                self.CurrentRoute.Stations[self.CurrentStation].ArrivalTime = arr
                self.CurrentRoute.Stations[self.CurrentStation].ArrivalSoundBuffer = arrsnd
                self.CurrentRoute.Stations[self.CurrentStation].DepartureTime = dep
                self.CurrentRoute.Stations[self.CurrentStation].DepartureSoundBuffer = depsnd
                self.CurrentRoute.Stations[self.CurrentStation].StopTime = halt
                self.CurrentRoute.Stations[self.CurrentStation].ForceStopSignal = True if stop == 1 else False
                self.CurrentRoute.Stations[self.CurrentStation].OpenLeftDoors = True \
                    if door == Direction.Left or door == Direction.Both else False
                self.CurrentRoute.Stations[self.CurrentStation].OpenRightDoors = True \
                    if door == Direction.Right or door == Direction.Both else False
                self.CurrentRoute.Stations[self.CurrentStation].SafetySystem = SafetySystem.Atc \
                    if device == 1 else SafetySystem.Ats
                self.CurrentRoute.Stations[self.CurrentStation].Stops = []

                self.CurrentRoute.Stations[self.CurrentStation].PassengerRatio = 0.01 * jam
                self.CurrentRoute.Stations[self.CurrentStation].TimetableDaytimeTexture = tdt
                self.CurrentRoute.Stations[self.CurrentStation].TimetableNighttimeTexture = tnt
                self.CurrentRoute.Stations[self.CurrentStation].DefaultTrackPosition = data.TrackPosition
                self.CurrentRoute.Stations[self.CurrentStation].ReopenDoor = 0.01 * reopen_door
                self.CurrentRoute.Stations[self.CurrentStation].ReopenStationLimit = reopen_station_limit
                self.CurrentRoute.Stations[self.CurrentStation].InterferenceInDoor = interference_in_door
                self.CurrentRoute.Stations[self.CurrentStation].MaxInterferingObjectRate = max_interfering_object_rate
                data.Blocks[block_index].Station = self.CurrentStation
                data.Blocks[block_index].StationPassAlarm = True if passalarm == 1 else False
                self.CurrentStop = -1
                self.DepartureSignalUsed = False
                # Detect common BVE2 / BVE4 dummy stations, missing names, etc.
                if (len(self.CurrentRoute.Stations[self.CurrentStation].Name) == 0) and (
                        self.CurrentRoute.Stations[self.CurrentStation].StopMode == StationStopMode.PlayerStop or
                        self.CurrentRoute.Stations[self.CurrentStation].StopMode == StationStopMode.AllStop):

                    if self.CurrentRoute.Stations[self.CurrentStation].OpenLeftDoors or \
                            self.CurrentRoute.Stations[self.CurrentStation].OpenRightDoors:
                        self.CurrentRoute.Stations[self.CurrentStation].Name = "Station " + str(self.CurrentStation + 1)

                    elif self.CurrentRoute.Stations[self.CurrentStation].ForceStopSignal:
                        self.CurrentRoute.Stations[self.CurrentStation].Dummy = True

            case TrackCommand.Station:
                self.CurrentStation += 1

                # Station 리스트가 존재하지 않거나 부족할 경우 확장
                if len(self.CurrentRoute.Stations) <= self.CurrentStation:
                    self.CurrentRoute.Stations.append(RouteStation())
                else:
                    self.CurrentRoute.Stations[self.CurrentStation] = RouteStation()

                # 인자가 있으면 이름 지정
                if len(arguments) >= 1 and len(arguments[0]) > 0:
                    self.CurrentRoute.Stations[self.CurrentStation].Name = arguments[0]

                if len(arguments) >= 2 and arguments[1].strip():
                    arg = arguments[1].strip()

                    if arg.lower() in ("p", "l"):
                        self.CurrentRoute.Stations[self.CurrentStation].StopMode = StationStopMode.AllPass

                    elif arg.lower() == "b":
                        self.CurrentRoute.Stations[self.CurrentStation].StopMode = StationStopMode.PlayerPass

                    elif arg.lower().startswith("b:"):
                        self.CurrentRoute.Stations[self.CurrentStation].StopMode = StationStopMode.PlayerPass
                        sucess, arr = self.try_parse_time(arg[2:].strip())
                        if not sucess:
                            logger.error(f"ArrivalTime is invalid in Track.Sta at line "
                                         f"{expression.Line}, column {expression.Column}, file {expression.File}")
                            arr = -1.0

                    elif arg.lower() == "s":
                        self.CurrentRoute.Stations[self.CurrentStation].StopMode = StationStopMode.PlayerStop

                    elif arg.lower().startswith("s:"):
                        self.CurrentRoute.Stations[self.CurrentStation].StopMode = StationStopMode.PlayerStop
                        sucess, arr = self.try_parse_time(arg[2:].strip())
                        if not sucess:
                            logger.error(f"ArrivalTime is invalid in Track.Sta at line "
                                         f"{expression.Line}, column {expression.Column}, file {expression.File}")
                            arr = -1.0

                    else:
                        sucess, arr = self.try_parse_time(arg)
                        if not sucess:
                            logger.error(f"ArrivalTime is invalid in Track.Sta at line "
                                         f"{expression.Line}, column {expression.Column}, file {expression.File}")
                            arr = -1.0

                if len(arguments) >= 3 and len(arguments[2]) > 0:
                    arg = arguments[2].strip()

                    if arg.lower() in ("t", "="):
                        self.CurrentRoute.Stations[self.CurrentStation].Type = StationType.Terminal

                    elif arg.lower().startswith("t:"):
                        self.CurrentRoute.Stations[self.CurrentStation].Type = StationType.Terminal
                        success, dep = self.try_parse_time(arg[2:].strip())
                        if not success:
                            logger.error(f"DepartureTime is invalid in Track.Sta at line {expression.Line},"
                                         f"column {expression.Column} in file {expression.File}")
                            dep = -1.0

                    elif arg.lower() == "c":
                        self.CurrentRoute.Stations[self.CurrentStation].Type = StationType.ChangeEnds

                    elif arg.lower().startswith("c:"):
                        self.CurrentRoute.Stations[self.CurrentStation].Type = StationType.ChangeEnds
                        success, dep = self.try_parse_time(arg[2:].strip())
                        if not success:
                            logger.error(f"DepartureTime is invalid in Track.Sta at line {expression.Line},"
                                         f"column {expression.Column} in file {expression.File}")
                            dep = -1.0

                    else:
                        success, dep = self.try_parse_time(arg)
                        if not success:
                            logger.error(f"DepartureTime is invalid in Track.Sta at line {expression.Line},"
                                         f"column {expression.Column} in file {expression.File}")
                            dep = -1.0
                stop = 0
                if len(arguments) >= 4 and len(arguments[3]) > 0:
                    success, stop = NumberFormats.try_parse_int_vb6(arguments[3])
                    if not success:
                        logger.error(f"ForcedRedSignal is invalid in Track.Sta at line {expression.Line},"
                                     f"column {expression.Column} in file {expression.File}")
                        stop = 0
                device = 0
                if len(arguments) >= 5 and len(arguments[4]) > 0:
                    if arguments[6].lower() == 'ats':
                        device = 0
                    elif arguments[6].lower() == 'atc':
                        device = 1
                    else:
                        success, device = NumberFormats.try_parse_int_vb6(arguments[4])
                        if not success:
                            logger.error(f'System is invalid in Track.Sta at line {expression.Line},'
                                         f"column {expression.Column} in file {expression.File}")
                            device = 0
                    if device != 0 and device != 1:
                        logger.error(f'System is not supported in Track.Sta at line {expression.Line},'
                                     f"column {expression.Column} in file {expression.File}")
                        device = 0

                depsnd = None

                if not preview_only:
                    if len(arguments) >= 6 and len(arguments[5]) != 0:

                        if Path.contains_invalid_chars(arguments[5]):
                            logger.error(f'DepartureSound contains illegal characters in{command} at line ,'
                                         f"{expression.Line} ,column {expression.Column} in file {expression.File}")
                        else:

                            f = os.path.join(self.SoundPath, arguments[5])
                            if not os.path.exists(f):
                                logger.error(f'DepartureSound {f} not found in Track.Sta at line {expression.Line},'
                                             f"column {expression.Column} in file {expression.File}")
                            else:
                                radius = 30.0
                                arrsnd = self.Plugin.CurrentHost.register_sound(f, radius)

                self.CurrentRoute.Stations[self.CurrentStation].ArrivalTime = arr
                self.CurrentRoute.Stations[self.CurrentStation].ArrivalSoundBuffer = None
                self.CurrentRoute.Stations[self.CurrentStation].DepartureTime = dep
                self.CurrentRoute.Stations[self.CurrentStation].DepartureSoundBuffer = depsnd
                self.CurrentRoute.Stations[self.CurrentStation].StopTime = 15.0
                self.CurrentRoute.Stations[self.CurrentStation].ForceStopSignal = True if stop == 1 else False
                self.CurrentRoute.Stations[self.CurrentStation].OpenLeftDoors = True
                self.CurrentRoute.Stations[self.CurrentStation].OpenRightDoors = True
                self.CurrentRoute.Stations[self.CurrentStation].SafetySystem = SafetySystem.Atc \
                    if device == 1 else SafetySystem.Ats
                self.CurrentRoute.Stations[self.CurrentStation].Stops = []

                self.CurrentRoute.Stations[self.CurrentStation].PassengerRatio = 1.0
                self.CurrentRoute.Stations[self.CurrentStation].TimetableDaytimeTexture = None
                self.CurrentRoute.Stations[self.CurrentStation].TimetableNighttimeTexture = None
                self.CurrentRoute.Stations[self.CurrentStation].DefaultTrackPosition = data.TrackPosition
                self.CurrentRoute.Stations[self.CurrentStation].ReopenDoor = 0.0
                self.CurrentRoute.Stations[self.CurrentStation].ReopenStationLimit = 0
                self.CurrentRoute.Stations[self.CurrentStation].InterferenceInDoor = 0.0
                self.CurrentRoute.Stations[self.CurrentStation].MaxInterferingObjectRate = 10
                data.Blocks[block_index].Station = self.CurrentStation
                data.Blocks[block_index].StationPassAlarm = False
                self.CurrentStop = -1
                self.DepartureSignalUsed = False
                # Detect common BVE2 / BVE4 dummy stations, missing names, etc.
                if (len(self.CurrentRoute.Stations[self.CurrentStation].Name) == 0) and (
                        self.CurrentRoute.Stations[self.CurrentStation].StopMode == StationStopMode.PlayerStop or
                        self.CurrentRoute.Stations[self.CurrentStation].StopMode == StationStopMode.AllStop):
                    # Set default name
                    self.CurrentRoute.Stations[self.CurrentStation].Name = f'Station {self.CurrentStation + 1}'
                    if self.CurrentRoute.Stations[self.CurrentStation].ForceStopSignal:
                        if self.IsRW:
                            '''
                            * NOTE: The Track.Sta command is not valid in RW format routes (and this is what allows the
                            * door direction to be set). Let's assume that no name and a forced red signal
                            * is actualy a signalling control station
                            * e.g. Rocky Mountains Express
                            *
                            * However, the Station format command can *also* be used in a CSV route,
                            * where according to the documentation, both doors are assumed to open. Assume that in this case
                            * it was deliberate....
                            '''
                            self.CurrentRoute.Stations[self.CurrentStation].Dummy = True
                            self.CurrentRoute.Stations[self.CurrentStation].Name = ''
                            self.CurrentRoute.Stations[self.CurrentStation].OpenLeftDoors = False
                            self.CurrentRoute.Stations[self.CurrentStation].OpenRightDoors = False

            case TrackCommand.StationXML:
                fn = os.path.join(os.path.dirname(filename), arguments[0])
                if not os.path.exists(fn):
                    logger.error(f'Station XML file {fn} not found in Track.StationXML at line '
                                 f"{expression.Line} ,column {expression.Column} in file {expression.File}")
                else:
                    self.CurrentStation += 1

                    # Station 리스트가 존재하지 않거나 부족할 경우 확장
                    if len(self.CurrentRoute.Stations) <= self.CurrentStation:
                        self.CurrentRoute.Stations.append(RouteStation())
                    else:
                        self.CurrentRoute.Stations[self.CurrentStation] = RouteStation()
                        sr = StopRequest(self.CurrentStation, 0, data.TrackPosition)
                        # self.CurrentRoute.Stations[self.CurrentStation] = StationXMLParser.ReadStationXML(CurrentRoute, fn, PreviewOnly, Data.TimetableDaytime, Data.TimetableNighttime, CurrentStation, ref Data.Blocks[BlockIndex].StationPassAlarm, ref sr);
                        if self.CurrentRoute.Stations[self.CurrentStation].Type == StationType.RequestStop:
                            data.RequestStops.append(sr)
                    data.Blocks[block_index].Station = self.CurrentStation

            case TrackCommand.Buffer:
                pass
            case TrackCommand.Form:
                pass
            case TrackCommand.Pole:
                if not preview_only:
                    idx = 0
                    if len(arguments) >= 1 and len(arguments[0]) > 0:
                        success, idx = NumberFormats.try_parse_int_vb6(arguments[0])
                        if not success:
                            logger.error(f'RailIndex is invalid in Track.Pole at line '
                                         f"{expression.Line} ,column {expression.Column} in file {expression.File}")
                            idx = 0
                    if idx < 0:
                        logger.error(f'RailIndex is expected to be non-negative in Track.Pole at line '
                                     f"{expression.Line} ,column {expression.Column} in file {expression.File}")
                    else:
                        if idx not in data.Blocks[block_index].Rails or not \
                                data.Blocks[block_index].Rails[idx].RailStarted:
                            logger.warning(f'RailIndex {idx} could be out of range in Track.Pole at line '
                                           f"{expression.Line} ,column {expression.Column} in file {expression.File}")
                        # Make sure RailPole is a list of proper RailPole objects
                        if idx >= len(data.Blocks[block_index].RailPole):
                            # Extend with *new* RailPole instances
                            missing = idx + 1 - len(data.Blocks[block_index].RailPole)
                            data.Blocks[block_index].RailPole.extend(Pole() for _ in range(missing))

                            # Now safe to assign
                            data.Blocks[block_index].RailPole[idx].Mode = 0
                            data.Blocks[block_index].RailPole[idx].Location = 0
                            data.Blocks[block_index].RailPole[idx].Interval = 2.0 * data.BlockInterval
                            data.Blocks[block_index].RailPole[idx].Type = 0

                        typ = data.Blocks[block_index].RailPole[idx].Mode
                        sttype = data.Blocks[block_index].RailPole[idx].Type
                        if len(arguments) >= 2 and len(arguments[1]) > 0:
                            success, typ = NumberFormats.try_parse_int_vb6(arguments[1])
                            if not success:
                                logger.error(f'AdditionalRailsCovered is invalid in Track.Pole at line '
                                             f"{expression.Line} ,column {expression.Column} in file {expression.File}")
                                typ = 0
                        if len(arguments) >= 3 and len(arguments[2]) > 0:
                            success, loc = NumberFormats.try_parse_double_vb6(arguments[2])
                            if not success:
                                logger.error(f'Location is invalid in Track.Pole at line '
                                             f"{expression.Line},"
                                             f"column {expression.Column} "
                                             f"in file {expression.File}")
                                loc = 0.0
                            data.Blocks[block_index].RailPole[idx].Location = loc

                        if len(arguments) >= 4 and len(arguments[3]) > 0:
                            success, dist = NumberFormats.try_parse_double_vb6(arguments[3], unit_of_lngth)
                            if not success:
                                logger.error(f'Interval is invalid in Track.Pole at line '
                                             f"{expression.Line},"
                                             f"column {expression.Column} "
                                             f"in file {expression.File}")
                                dist = data.BlockInterval

                            data.Blocks[block_index].RailPole[idx].Interval = dist

                        if len(arguments) >= 5 and len(arguments[4]) > 0:
                            success, sttype = NumberFormats.try_parse_int_vb6(arguments[4])
                            if not success:
                                logger.error(f'PoleStructureIndex is invalid in Track.Pole at line '
                                             f"{expression.Line},"
                                             f"column {expression.Column} "
                                             f"in file {expression.File}")
                                sttype = 0

                        if typ < 0 or typ not in data.Structure.Poles or data.Structure.Poles[typ] is None:
                            logger.error(f'PoleStructureIndex {typ} references an object '
                                         f'not loaded in Track.Pole at line '
                                         f"{expression.Line},"
                                         f"column {expression.Column} "
                                         f"in file {expression.File}")
                        elif sttype < 0 or sttype not in data.Structure.Poles[typ] or \
                                data.Structure.Poles[typ][sttype] is None:
                            logger.error(f'PoleStructureIndex {typ} references an object '
                                         f'not loaded in Track.Pole at line '
                                         f"{expression.Line},"
                                         f"column {expression.Column} "
                                         f"in file {expression.File}")
                        else:
                            data.Blocks[block_index].RailPole[idx].Mode = typ
                            data.Blocks[block_index].RailPole[idx].Type = sttype
                            data.Blocks[block_index].RailPole[idx].Exists = True

            case TrackCommand.PoleEnd:
                if not preview_only:
                    idx = 0
                    if len(arguments) >= 1 and len(arguments[0]) > 0:
                        success, idx = NumberFormats.try_parse_int_vb6(arguments[0])
                        if not success:
                            logger.error(f'RailIndex is invalid in Track.Pole at line '
                                         f"{expression.Line} ,column {expression.Column} in file {expression.File}")
                            idx = 0

                    if idx < 0 or idx >= len(data.Blocks[block_index].RailPole):
                        logger.error(f'RailIndex {idx} does not reference an existing pole in Track.PoleEnd at line '
                                     f"{expression.Line} ,column {expression.Column} in file {expression.File}")
                    else:
                        if idx not in data.Blocks[block_index].Rails or \
                                not data.Blocks[block_index].Rails[idx].RailStarted and \
                                not data.Blocks[block_index].Rails[idx].RailEnded:
                            logger.warning(
                                f'RailIndex {idx} could be out of range in Track.PoleEnd at line '
                                f"{expression.Line} ,column {expression.Column} in file {expression.File}")

                        data.Blocks[block_index].RailPole[idx].Exists = False
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
                if not preview_only:
                    if len(arguments) < 2:
                        '''
                        /*
                        * If no / one arguments are supplied, this previously produced FreeObject 0 dropped on either
                        * Rail 0 (no arguments) or on the rail specified by the first argument.
                        *
                         * BVE4 ignores these, and we should too.
                        */
                        '''
                        logger.error(f'An insufficient number of arguments was supplied in Track.FreeObj at line '
                                     f"{expression.Line} ,column {expression.Column} in file {expression.File}")
                        return data
                    idx, sttype = 0, 0
                    if len(arguments) >= 1 and len(arguments[0]) > 0:
                        success, idx = NumberFormats.try_parse_int_vb6(arguments[0])
                        if not success:
                            logger.error(f'RailIndex is invalid in Track.FreeObj at line '
                                         f"{expression.Line} ,column {expression.Column} in file {expression.File}")
                            idx = 0
                    if len(arguments) >= 2 and len(arguments[1]) > 0:
                        success, sttype = NumberFormats.try_parse_int_vb6(arguments[1])
                        if not success:
                            logger.error(f'FreeObjStructureIndex is invalid in Track.FreeObj at line '
                                         f"{expression.Line} ,column {expression.Column} in file {expression.File}")
                            sttype = 0
                    if idx < -1:
                        logger.error(f'RailIndex is expected to be non-negative or -1 in Track.FreeObj at line '
                                     f"{expression.Line} ,column {expression.Column} in file {expression.File}")
                    elif sttype < 0:
                        logger.error(f'FreeObjStructureIndex is expected to be non-negative in Track.FreeObj at line '
                                     f"{expression.Line} ,column {expression.Column} in file {expression.File}")
                    else:
                        if idx >= 0 and idx not in data.Blocks[block_index].Rails or not \
                                data.Blocks[block_index].Rails[idx].RailStarted:
                            logger.warning(f'RailIndex {idx} could be out of range in Track.FreeObj at line '
                                           f"{expression.Line} ,column {expression.Column} in file {expression.File}")

                        if sttype not in data.Structure.FreeObjects:
                            logger.error(f'FreeObjStructureIndex {sttype} references an object '
                                         f'not loaded in Track.FreeObj at line Track.FreeObj at line '
                                         f"{expression.Line} ,column {expression.Column} in file {expression.File}")
                        else:
                            from OpenBveApi.Math.Vectors.Vector2 import Vector2
                            objectPosition = Vector2()
                            yaw, pitch, roll = 0.0, 0.0, 0.0
                            if len(arguments) >= 3 and len(arguments[2]) > 0:
                                success, objectPosition.x = NumberFormats.try_parse_double_vb6(arguments[2], unit_of_lngth)
                                if not success:
                                    logger.error(f'X is invalid in Track.FreeObj at line '
                                                 f"{expression.Line} ,column {expression.Column} in file {expression.File}")
                            if len(arguments) >= 4 and len(arguments[3]) > 0:
                                success, objectPosition.y = NumberFormats.try_parse_double_vb6(arguments[3], unit_of_lngth)
                                if not success:
                                    logger.error(f'Y is invalid in Track.FreeObj at line '
                                                 f"{expression.Line} ,column {expression.Column} in file {expression.File}")

                            if len(arguments) >= 5 and len(arguments[4]) > 0:
                                success, yaw = NumberFormats.try_parse_double_vb6(arguments[4])
                                if not success:
                                    logger.error(f'Yaw is invalid in Track.FreeObj at line '
                                                 f"{expression.Line} ,column {expression.Column} in file {expression.File}")
                            if len(arguments) >= 6 and len(arguments[5]) > 0:
                                success, pitch = NumberFormats.try_parse_double_vb6(arguments[5])
                                if not success:
                                    logger.error(f'Pitch is invalid in Track.FreeObj at line '
                                                 f"{expression.Line} ,column {expression.Column} in file {expression.File}")
                            if len(arguments) >= 7 and len(arguments[6]) > 0:
                                success, roll = NumberFormats.try_parse_double_vb6(arguments[6])
                                if not success:
                                    logger.error(f'Roll is invalid in Track.FreeObj at line '
                                                 f"{expression.Line} ,column {expression.Column} in file {expression.File}")
                            if idx == -1:
                                if not data.ignore_pitch_roll:
                                    data.Blocks[block_index].GroundFreeObj.append(
                                        FreeObj(
                                            data.TrackPosition,
                                            sttype,
                                            objectPosition,
                                            math.radians(yaw),
                                            math.radians(pitch),
                                            math.radians(roll)
                                        )
                                    )

                                else:
                                    data.Blocks[block_index].GroundFreeObj.append(
                                        FreeObj(
                                            data.TrackPosition,
                                            sttype,
                                            objectPosition,
                                            math.radians(yaw)
                                        )
                                    )
                            else:
                                if idx not in data.Blocks[block_index].RailFreeObj:
                                    data.Blocks[block_index].RailFreeObj[idx] = []
                                if not data.ignore_pitch_roll:
                                    data.Blocks[block_index].RailFreeObj[idx].append(
                                        FreeObj(
                                            data.TrackPosition,
                                            sttype,
                                            objectPosition,
                                            math.radians(yaw),
                                            math.radians(pitch),
                                            math.radians(roll)
                                        )
                                    )
                                else:
                                    data.Blocks[block_index].RailFreeObj[idx].append(
                                        FreeObj(
                                            data.TrackPosition,
                                            sttype,
                                            objectPosition,
                                            math.radians(yaw)
                                        )
                                    )
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
