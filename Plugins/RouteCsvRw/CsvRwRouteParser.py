import math
from typing import List
import time

from uitl import Util, RecursiveEncoder

from RouteManager2.Climate.Fog import Fog
from RouteManager2.CurrentRoute import CurrentRoute
from RouteManager2.Stations.RouteStation import RouteStation
from .ApplyRouteData import Parser8
from .Compatability.RoutefilePatch import Parser3
from .Namespaces.NonTrack.Options import Parser5
from .Namespaces.NonTrack.OptionsCommands import OptionsCommand
from .Namespaces.NonTrack.Route import Parser6
from .Namespaces.NonTrack.RouteCommands import RouteCommand
from .Namespaces.Track.Track import Parser7

from .PreprocessOptions import Parser2
from .Functions import Parser4
from .RouteData import RouteData
from .Preprocess import Parser1
from OpenBveApi.Objects.ObjectInterface import ObjectInterface, CompatabilityHacks
from OpenBveApi.Routes.TrackDirection import TrackDirection
from Plugins.RouteCsvRw.Structures.Trains.StopRequest import StopRequest
from .Namespaces.Track.TrackCommands import TrackCommand
from OpenBveApi.Routes.ObjectDisposalMode import ObjectDisposalMode
from OpenBveApi.Colors.Color24 import Color24
from .Structures.Expression import Expression
from OpenBveApi.Math.Math import NumberFormats


class Parser(Parser1, Parser2, Parser3, Parser4, Parser5, Parser6, Parser7, Parser8):
    EnabledHacks: CompatabilityHacks = None

    def __init__(self):
        super().__init__()
        self.ObjectPath: str = ''
        self.SoundPath: str = ''
        self.TrainPath: str = ''
        self.CompatibilityFolder: str = ''
        self.IsRW: bool = False
        self.IsHmmsim: bool = False
        self.CurrentRoute: CurrentRoute = None
        self.Plugin: 'Plugin' = None  # 여긴 직접 생성 X
        self.AllowTrackPositionArguments = False
        self.SplitLineHack = True

    from .Plugin import Plugin
    def parse_route(self, file_name: str, is_rw: bool, encoding: str, train_path: str,
                    object_path: str, sound_path: str, preview_only: bool, host_plugin: "Plugin"):
        self.Plugin = host_plugin

        self.CurrentRoute = host_plugin.CurrentRoute

        # Store paths for later use
        self.ObjectPath = object_path
        self.SoundPath = sound_path
        self.TrainPath = train_path
        self.IsRW = is_rw

        freeobj_count = 0
        railtype_count = 0
        self.Plugin.CurrentOptions.UnitOfSpeed = "km/h"
        self.Plugin.CurrentOptions.SpeedConversionFactor = 0.0

        self.Plugin.CurrentOptions.ObjectDisposalMode = ObjectDisposalMode.Legacy

        data = RouteData(preview_only)
        if not preview_only:
            data.Blocks[0].Background = 0
            data.Blocks[0].Fog = Fog(CurrentRoute.NoFogStart, CurrentRoute.NoFogEnd, Color24.Grey, 0)

        data = self.parse_route_for_data(file_name, encoding, data, preview_only)

        if self.Plugin.Cancel:
            self.Plugin.IsLoading = False
            return
        data = self.apply_route_data(file_name, data, preview_only)

        # json dump후 확인
        RecursiveEncoder.save(r'c:\temp\route_data.json', data, False)

    def parse_route_for_data(self, file_name: str, encoding: str, data: RouteData,
                             preview_only: bool) -> RouteData:
        with open(file_name, 'r', encoding=encoding) as f:
            lines: List[str] = f.readlines()
        start_time = time.time()
        expressions = self.preprocess_split_into_expressions(file_name, lines, True)
        expressions = self.preprocess_chr_rnd_sub(file_name, encoding, expressions)
        unit_of_length = [1.0]
        # Set units of speed initially to km/h
        # This represents 1km/h in m/s
        data.UnitOfSpeed = 0.277777777777778
        data = self.pre_process_options(expressions, data, unit_of_length, preview_only)
        expressions = self.preprocess_sort_by_track_position(unit_of_length, expressions)
        data = self.parse_route_for_data2(file_name, encoding, expressions, unit_of_length, data, preview_only)
        self.CurrentRoute.UnitOfLength = unit_of_length
        end_time = time.time()
        elapsed = end_time - start_time

        # 익스프레션추출 테스트
        Util.test(expressions)

        return data

    freeObjCount: int = 0
    missingObjectCount: int = 0
    railtypeCount: int = 0

    # parse route for data
    def parse_route_for_data2(self, file_name: str, encoding: str, expressions: List["Expression"],
                              unit_of_length: list[float], data: RouteData, preview_only: bool) -> RouteData | None:
        current_station = -1
        current_stop = -1
        current_section = 0

        section = ""
        section_always_prefix = False
        block_index = 0

        self.CurrentRoute.Tracks[0].Direction = TrackDirection.Forwards
        self.CurrentRoute.Stations: List[RouteStation] = []

        data.RequestStops = List[StopRequest]
        progress_factor = 0.3333 if len(expressions) == 0 else 0.3333 / len(expressions)
        # process non-track namespaces
        # Check for any special-cased fixes we might need
        self.check_for_available_patch(file_name, data, expressions, preview_only)
        # Apply parameters to object loaders

        for j in range(len(expressions)):
            self.Plugin.CurrentProgress = j * progress_factor
            if j & 255 == 0:
                # time.sleep(1)
                if self.Plugin.Cancel:
                    self.Plugin.IsLoading = False
                    return
            if expressions[j].Text.startswith('[') and expressions[j].Text.endswith(']'):
                section = expressions[j].Text[1:-1].strip()
                if section.lower() == "object":
                    section = "Structure"
                elif section.lower() == "railway":
                    section = "Track"
                section_always_prefix = True
            else:
                if self.IsRW:
                    expressions[j].convert_rw_to_csv(section, section_always_prefix)

                # separate command and arguments
                command, argument_sequence = expressions[j].separate_commands_and_arguments(None, False,
                                                                                            self.IsRW, section)

                # process command
                number_check = not self.IsRW or section.lower() == "track"

                success = NumberFormats.is_valid_double(command, unit_of_length)
                if number_check and success:
                    # track position (ignored)
                    pass
                else:
                    arguments = self.split_arguments(argument_sequence)

                    # preprocess command
                    if command.lower() == 'with':
                        if len(arguments) >= 1:
                            section = arguments[0]
                            section_always_prefix = False
                        else:
                            section = ''
                            section_always_prefix = False

                        command = ''
                    else:
                        if command.startswith('.'):
                            command = section + command
                        elif section_always_prefix:
                            command = section + '.' + command
                        command = command.replace('.Void', '')

                        if command.lower().startswith("structure") and command.lower().endswith(".load"):
                            command = command[:-5].rstrip()
                        elif command.lower().startswith("texture.background") and command.lower().endswith(".load"):
                            command = command[:-5].rstrip()
                        elif command.lower().startswith("texture.background") and command.lower().endswith(".x"):
                            command = "texture.backgroundx" + command[18:-2].rstrip()
                        elif command.lower().startswith("texture.background") and command.lower().endswith(".aspect"):
                            command = "texture.backgroundaspect" + command[18:-7].rstrip()
                        elif command.lower().startswith("structure.back") and command.lower().endswith(".x"):
                            command = "texture.backgroundx" + command[14:-2].rstrip()
                        elif command.lower().startswith("structure.back") and command.lower().endswith(".aspect"):
                            command = "texture.backgroundaspect" + command[14:-7].rstrip()
                        elif command.lower().startswith("cycle") and command.lower().endswith(".params"):
                            command = command[:-7].rstrip()
                        elif command.lower().startswith("signal") and command.lower().endswith(".load"):
                            command = command[:-5].rstrip()
                        elif command.lower().startswith("train.run") and command.lower().endswith(".set"):
                            command = command[:-4].rstrip()
                        elif command.lower().startswith("train.flange") and command.lower().endswith(".set"):
                            command = command[:-4].rstrip()
                        elif command.lower().startswith("train.timetable") and command.lower().endswith(".day.load"):
                            command = "train.timetable.day" + command[15:-9].strip()
                        elif command.lower().startswith("train.timetable") and command.lower().endswith(".night.load"):
                            command = "train.timetable.night" + command[15:-11].strip()
                        elif command.lower().startswith("train.timetable") and command.lower().endswith(".day"):
                            command = "train.timetable.day" + command[15:-4].strip()
                        elif command.lower().startswith("train.timetable") and command.lower().endswith(".night"):
                            command = "train.timetable.night" + command[15:-6].strip()
                        elif command.lower().startswith("route.signal") and command.lower().endswith(".set"):
                            command = command[:-4].rstrip()
                        elif command.lower().startswith("route.runinterval"):
                            command = "train.interval" + command[17:]
                        elif command.lower().startswith("train.gauge"):
                            command = "route.gauge" + command[11:]
                        elif command.lower().startswith("texture."):
                            command = "structure." + command[8:]

                        # Needed after the initial processing to make the enum parse work
                        command = command.replace("timetable.day", "timetableday")
                        command = command.replace("timetable.night", "timetablenight")

                    command_indices = self.find_indices(command, expressions[j])

                    # process command
                    if not command.isspace():
                        period = command.find('.')
                        name_space = ''
                        if period != 1:
                            name_space = command[:period].lower()
                            command = command[period + 1:]
                        command = command.lower()

                        match name_space:
                            case 'options':
                                parsed_option_command, success = Util.try_parse_enum(OptionsCommand, command)
                                if success:
                                    data = self.parse_option_command(parsed_option_command, arguments, unit_of_length,
                                                                     expressions[j], data, preview_only)
                                else:
                                    print(f'Unrecognised command {command} encountered in the Options namespace at line'
                                          f'{expressions[j].Line} , column {expressions[j].Column}'
                                          f' in file {expressions[j].File}')
                            case 'route':
                                parsed_route_command, success = Util.try_parse_enum(RouteCommand, command)
                                if success:
                                    data = self.parse_route_command(parsed_route_command, arguments, command_indices[0],
                                                                    file_name,
                                                                    unit_of_length, expressions[j], data, preview_only)
                                else:
                                    print(f'Unrecognised command {command} encountered in the Route namespace at line'
                                          f'{expressions[j].Line} , column {expressions[j].Column}'
                                          f' in file {expressions[j].File}')
                            case "train":
                                pass
                            case "structure":
                                pass
                            case "texture":
                                pass
                            case "":
                                pass
                            case "cycle":
                                pass
                            case "track":
                                pass
                            case _:
                                pass
        # process track namespace
        for j in range(len(expressions)):
            self.Plugin.CurrentProgress = 0.3333 + j * progress_factor
            if j & 255 == 0:
                # time.sleep(1)
                if self.Plugin.Cancel:
                    self.Plugin.IsLoading = False
                    return
            if data.line_ending_fix:
                if expressions[j].Text.endswith('_'):
                    expressions[j].Text = expressions[j].Text[:-1].strip()
            if expressions[j].Text.startswith('[') and expressions[j].Text.endswith(']'):
                section = expressions[j].Text[1:-1].strip()
                if section.lower() == "object":
                    section = "Structure"
                elif section.lower() == "railway":
                    section = "Track"
                section_always_prefix = True
            else:
                if self.IsRW:
                    expressions[j].convert_rw_to_csv(section, section_always_prefix)
                # separate command and arguments
                command, argument_sequence = expressions[j].separate_commands_and_arguments(
                    None, False, self.IsRW, section)
                # process command
                number_check = not self.IsRW or section.lower() == "track"
                success, current_track_position = NumberFormats.try_parse_double(command, unit_of_length)
                if number_check and success:
                    # track position
                    if len(argument_sequence) != 0:
                        print(f'A track position must not contain any arguments at line '
                              f'{expressions[j].Line} , column {expressions[j].Column}'
                              f' in file {expressions[j].File}')
                        if self.AllowTrackPositionArguments:
                            data.TrackPosition = current_track_position
                            block_index = int(math.floor(current_track_position / data.BlockInterval + 0.001))
                            if data.FirstUsedBlock == -1:
                                data.FirstUsedBlock = block_index
                            data.create_missing_blocks(block_index, preview_only)
                    elif current_track_position < 0.0:
                        print(f'Negative track position encountered at line '
                              f'{expressions[j].Line} , column {expressions[j].Column}'
                              f' in file {expressions[j].File}')
                    else:
                        if self.Plugin.CurrentOptions.EnableBveTsHacks and \
                                self.IsRW \
                                and current_track_position == 4535545100:
                            # WMATA Red line has an erroneous track position causing an out of memory cascade
                            current_track_position = 45355
                        data.TrackPosition = current_track_position
                        block_index = int(math.floor(current_track_position / data.BlockInterval + 0.001))
                        if data.FirstUsedBlock == -1:
                            data.FirstUsedBlock = block_index
                        data.create_missing_blocks(block_index, preview_only)
                else:
                    arguments = self.split_arguments(argument_sequence)

                    # preprocess command
                    if command.lower() == "with":
                        if len(arguments) >= 1:
                            section = arguments[0]
                            section_always_prefix = False
                        else:
                            section = ''
                            section_always_prefix = False
                        command = ''
                    else:
                        if command.startswith('.'):
                            command = section + command
                        elif section_always_prefix:
                            command = section + '.' + command
                        command = command.replace('.Void', '')

                    # process command
                    if not command.isspace():
                        period = command.find('.')
                        name_space = ''
                        if period != 1:
                            name_space = command[:period].lower()
                            command = command[period + 1:]
                        if name_space.lower().startswith('signal'):
                            name_space = ''
                        command = command.lower()

                        match name_space:
                            case 'track':
                                parsed_command, success = Util.try_parse_enum(TrackCommand, command)
                                if success:
                                    data = self.parse_track_command(parsed_command, arguments, file_name,
                                                                    unit_of_length,
                                                                    expressions[j], data, block_index, preview_only,
                                                                    self.IsRW)
                                else:
                                    if self.IsHmmsim:
                                        period = command.find('.')
                                        railkey = command[:period]
                                        railindex = len(data.RailKeys)
                                        if railkey in data.RailKeys:
                                            railindex = data.RailKeys[railkey]
                                        else:
                                            data.RailKeys[railkey] = railindex
                                        command = command[period + 1:]
                                        parsed_command, success = Util.try_parse_enum(TrackCommand, command)
                                        if success:
                                            data = self.parse_track_command(command, arguments, file_name,
                                                                            unit_of_length,
                                                                            expressions[j], data, block_index,
                                                                            preview_only, self.IsRW)
                                        else:
                                            print(f'Hmmsim: Unrecognised command {command} encountered in the Route'
                                                  f' namespace at line {expressions[j].Line}, '
                                                  f'column {expressions[j].Column} '
                                                  f'in file {expressions[j].File}')
                                    else:
                                        print(f'OpenBVE: Unrecognised command {command} encountered in the Route '
                                              f'namespace at line {expressions[j].Line}, '
                                              f'column {expressions[j].Column} '
                                              f'in file {expressions[j].File}')
                            case "options":
                                pass
                            case "route":
                                pass
                            case "train":
                                pass
                            case "structure":
                                pass
                            case "texture":
                                pass
                            case '':
                                pass
                            case "cycle":
                                pass
                            case _:
                                print(f'The command {command} is not supported at line {expressions[j].Line}, '
                                      f'column {expressions[j].Column} in file {expressions[j].File}')
        return data
