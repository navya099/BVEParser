from RouteManager2.CurrentRoute import CurrentRoute
from RouteManager2.Stations.RouteStation import RouteStation
from .Compatability.RoutefilePatch import Parser3
from .PreprocessOptions import Parser2
from .RouteData import RouteData
from .Preprocess import Parser1
from OpenBveApi.Objects.ObjectInterface import ObjectInterface, CompatabilityHacks
from typing import List
from tqdm import tqdm
import time
from OpenBveApi.Routes.TrackDirection import TrackDirection
from Plugins.RouteCsvRw.Structures.Trains.StopRequest import StopRequest


class Parser(Parser1, Parser2, Parser3):
    EnabledHacks = CompatabilityHacks()

    def __init__(self):
        super().__init__()
        self.ObjectPath = ''
        self.SoundPath = ''
        self.TrainPath = ''
        self.CompatibilityFolder = ''
        self.IsRW = None
        self.IsHmmsim = None
        self.CurrentRoute = CurrentRoute()
        self.Plugin = None  # 여긴 직접 생성 X
        self.AllowTrackPositionArguments = False
        self.SplitLineHack = True

    def parse_route(self, file_name, is_rw, encoding, train_path, object_path, sound_path, preview_only, host_plugin):
        self.Plugin = host_plugin
        self.CurrentRoute = self.Plugin.CurrentRoute
        self.ObjectPath = object_path
        self.SoundPath = sound_path
        self.TrainPath = train_path
        self.IsRW = is_rw

        freeobj_count = 0
        railtype_count = 0
        data = RouteData(preview_only)

        self.parse_route_for_data(file_name, encoding, data, preview_only)

        if self.Plugin.Cancel:
            self.Plugin.IsLoading = False
            return
        self.apply_route_data(file_name, data, preview_only)

    def parse_route_for_data(self, file_name, encoding, data, preview_only):
        with open(file_name, 'r', encoding=encoding) as f:
            lines: List[str] = f.readlines()
        start_time = time.time()
        expressions = self.preprocess_split_into_expressions(file_name, lines, True)
        expressions = self.preprocess_chr_rnd_sub(file_name, encoding, expressions)
        print('루프탈출')
        unit_of_length = [1.0]
        # Set units of speed initially to km/h
        # This represents 1km/h in m/s
        data.UnitOfSpeed = 0.277777777777778
        data = self.pre_process_options(expressions, data, unit_of_length, preview_only)
        expressions = self.preprocess_sort_by_track_position(unit_of_length, expressions)
        data = self.parse_route_for_data2(file_name, encoding, expressions, unit_of_length, data, preview_only)
        print('정렬성공')
        end_time = time.time()
        elapsed = end_time - start_time

        test(expressions)
        print('테스트성공')

    def parse_route_for_data2(self, file_name: str, encoding: str, expressions: List[Expression],
                              unit_of_length: [float], data: RouteData, preview_only: bool) -> RouteData:
        current_station = -1
        current_stop = -1
        current_section = 0

        section = ""
        section_always_prefix = False
        block_index = 0

        self.CurrentRoute.Tracks[0].Direction = TrackDirection.Forwards
        self.CurrentRoute.Stations = List[RouteStation]

        data.RequestStops = List[StopRequest]
        progress_factor = 0.3333 if len(expressions) == 0 else 0.3333 / len(expressions)
        # process non-track namespaces
        # Check for any special-cased fixes we might need

    @staticmethod
    def apply_route_data(file_name, data, preview_only):
        pass


def test(Expressions):
    with open("C:/TEMP/expressions_all.txt", "w", encoding="utf-8") as f:
        for i in range(len(Expressions)):
            f.write(
                f"{i} , {Expressions[i].Line} , {Expressions[i].Text}, {Expressions[i].TrackPositionOffset}, {Expressions[i].File}\n")
    pass
